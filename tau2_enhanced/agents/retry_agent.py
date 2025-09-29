"""
RetryManagedLLMAgent: Agent with intelligent retry logic for validation errors.

This agent extends the base LLMAgent to handle validation errors with a 3-attempt
retry mechanism, addressing the 87% action execution failure rate identified
in the tau2-bench analysis.
"""

import time
import copy
import re
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from tau2.agent.llm_agent import LLMAgent
from tau2.data_model.message import Message, SystemMessage
from tau2_enhanced.logging import ExecutionLogger


@dataclass
class RetryAttempt:
    """Information about a single retry attempt."""
    attempt_number: int
    error_type: str
    error_message: str
    recovery_strategy: str
    tool_args_modified: Dict[str, Any]
    timestamp: float
    success: bool = False


@dataclass
class RetrySequence:
    """Complete retry sequence for a failed operation."""
    tool_name: str
    original_args: Dict[str, Any]
    attempts: List[RetryAttempt]
    final_success: bool
    total_duration: float
    recovery_strategies_used: List[str]


class ValidationError(Exception):
    """Custom exception for validation errors that can be retried."""
    def __init__(self, message: str, details: Optional[Dict] = None, expected_format: Optional[str] = None):
        super().__init__(message)
        self.details = details or {}
        self.expected_format = expected_format


class RetryManagedLLMAgent(LLMAgent):
    """
    Agent with intelligent retry logic for validation errors.

    This agent intercepts tool execution failures, analyzes the error type,
    and applies appropriate recovery strategies with up to 3 retry attempts.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_retries = 3
        self.retry_delay_base = 0.5  # Base delay in seconds
        self.retry_sequences: List[RetrySequence] = []

        # Initialize execution logger for retry tracking
        self.retry_logger = ExecutionLogger(
            log_file=None,  # Will be set by environment if needed
            auto_flush=True,
            console_output=False
        )

        # Error pattern recognition for recovery strategy selection
        self.error_patterns = {
            'type_mismatch': [
                r'expected .* got .*',
                r'invalid type.*expected',
                r'type.*not supported'
            ],
            'missing_parameter': [
                r'missing required parameter',
                r'required argument.*missing',
                r'missing.*required'
            ],
            'invalid_format': [
                r'invalid format',
                r'format error',
                r'malformed.*format',
                r'incorrect format'
            ],
            'value_out_of_range': [
                r'out of range',
                r'invalid value',
                r'value.*not allowed',
                r'exceeds.*limit'
            ],
            'enum_violation': [
                r'not in allowed values',
                r'invalid choice',
                r'must be one of',
                r'unknown.*option'
            ]
        }

    def generate_next_message(self, message, state):
        """
        Override to add retry logic for tool execution failures.

        This method wraps the original message generation with retry logic
        that can recover from validation errors in tool calls.
        """
        try:
            return super().generate_next_message(message, state)
        except Exception as e:
            # Check if this is a retryable validation error
            if self._is_retryable_error(e):
                return self._handle_retry_scenario(message, state, e)
            else:
                # Re-raise non-retryable errors
                raise

    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable based on its type and message.

        Args:
            error: The exception that occurred

        Returns:
            True if the error can be retried with modifications
        """
        error_message = str(error).lower()
        error_type = type(error).__name__

        # Common retryable error patterns
        retryable_patterns = [
            'validation', 'parameter', 'argument', 'format',
            'type', 'value', 'range', 'choice', 'required'
        ]

        # Check if error message contains retryable keywords
        for pattern in retryable_patterns:
            if pattern in error_message:
                return True

        # Check specific error types that are usually retryable
        retryable_types = [
            'ValidationError', 'ValueError', 'TypeError',
            'KeyError', 'AttributeError'
        ]

        return error_type in retryable_types

    def _handle_retry_scenario(self, message, state, original_error: Exception):
        """
        Handle a retry scenario with intelligent error recovery.

        Args:
            message: Original message that caused the error
            state: Current conversation state
            original_error: The error that triggered the retry

        Returns:
            Result from successful retry or re-raises final error
        """
        retry_sequence = RetrySequence(
            tool_name="unknown",  # Will be updated if we can extract it
            original_args={},
            attempts=[],
            final_success=False,
            total_duration=0,
            recovery_strategies_used=[]
        )

        start_time = time.time()

        for attempt in range(self.max_retries):
            try:
                # Create retry attempt record
                retry_attempt = RetryAttempt(
                    attempt_number=attempt + 1,
                    error_type=type(original_error).__name__,
                    error_message=str(original_error),
                    recovery_strategy="",
                    tool_args_modified={},
                    timestamp=time.time(),
                    success=False
                )

                # Determine recovery strategy
                recovery_strategy = self._determine_recovery_strategy(original_error)
                retry_attempt.recovery_strategy = recovery_strategy
                retry_sequence.recovery_strategies_used.append(recovery_strategy)

                # Apply recovery strategy to the conversation state
                modified_state = self._apply_recovery_strategy(
                    state, original_error, recovery_strategy, attempt
                )

                # Add retry guidance message to conversation
                retry_guidance = self._create_retry_guidance_message(
                    original_error, recovery_strategy, attempt + 1
                )
                modified_state.messages.append(retry_guidance)

                # Log retry attempt
                self.retry_logger.log_context_reduction(
                    original_tokens=len(state.messages),
                    reduced_tokens=len(modified_state.messages),
                    reduction_strategy=f"retry_guidance_{recovery_strategy}",
                    information_preserved=True,
                    performance_impact=retry_attempt.timestamp - start_time
                )

                # Attempt the operation again
                result = super().generate_next_message(message, modified_state)

                # Success! Record and return
                retry_attempt.success = True
                retry_sequence.attempts.append(retry_attempt)
                retry_sequence.final_success = True
                retry_sequence.total_duration = time.time() - start_time

                self.retry_sequences.append(retry_sequence)

                # Log successful retry
                self.retry_logger.log_tool_execution(
                    tool_name=f"retry_recovery_{attempt + 1}",
                    success=True,
                    execution_time=retry_sequence.total_duration,
                    tool_args={
                        "original_error": str(original_error),
                        "recovery_strategy": recovery_strategy,
                        "attempts": attempt + 1
                    },
                    result={"retry_success": True, "final_attempt": attempt + 1}
                )

                return result

            except Exception as e:
                # This attempt failed
                retry_attempt.error_message = str(e)
                retry_attempt.error_type = type(e).__name__
                retry_sequence.attempts.append(retry_attempt)

                if attempt < self.max_retries - 1:
                    # Not the final attempt, wait and continue
                    delay = self.retry_delay_base * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
                    original_error = e  # Update error for next attempt
                else:
                    # Final attempt failed
                    retry_sequence.final_success = False
                    retry_sequence.total_duration = time.time() - start_time
                    self.retry_sequences.append(retry_sequence)

                    # Log final failure
                    self.retry_logger.log_tool_execution(
                        tool_name=f"retry_failure_final",
                        success=False,
                        execution_time=retry_sequence.total_duration,
                        tool_args={
                            "original_error": str(original_error),
                            "strategies_tried": retry_sequence.recovery_strategies_used,
                            "total_attempts": self.max_retries
                        },
                        error_message=str(e),
                        error_type=type(e).__name__
                    )

                    # Re-raise the final error
                    raise

    def _determine_recovery_strategy(self, error: Exception) -> str:
        """
        Determine the best recovery strategy based on the error type and message.

        Args:
            error: The error that occurred

        Returns:
            String identifier for the recovery strategy to use
        """
        error_message = str(error).lower()

        # Check error patterns to classify the error type
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message):
                    return self._get_strategy_for_error_type(error_type)

        # Fallback strategy
        return 'generic_simplification'

    def _get_strategy_for_error_type(self, error_type: str) -> str:
        """
        Get the recovery strategy for a specific error type.

        Args:
            error_type: Classified error type

        Returns:
            Recovery strategy identifier
        """
        strategy_map = {
            'type_mismatch': 'type_correction',
            'missing_parameter': 'parameter_completion',
            'invalid_format': 'format_correction',
            'value_out_of_range': 'value_adjustment',
            'enum_violation': 'enum_correction'
        }

        return strategy_map.get(error_type, 'generic_simplification')

    def _apply_recovery_strategy(self, state, error: Exception, strategy: str, attempt: int):
        """
        Apply a recovery strategy to modify the conversation state.

        Args:
            state: Current conversation state
            error: The error that occurred
            strategy: Recovery strategy to apply
            attempt: Current attempt number (0-indexed)

        Returns:
            Modified conversation state
        """
        # Create a copy of the state to modify
        modified_state = copy.deepcopy(state)

        # Apply strategy-specific modifications
        if strategy == 'parameter_completion':
            return self._apply_parameter_completion(modified_state, error)
        elif strategy == 'type_correction':
            return self._apply_type_correction(modified_state, error)
        elif strategy == 'format_correction':
            return self._apply_format_correction(modified_state, error)
        elif strategy == 'value_adjustment':
            return self._apply_value_adjustment(modified_state, error)
        elif strategy == 'enum_correction':
            return self._apply_enum_correction(modified_state, error)
        else:
            return self._apply_generic_simplification(modified_state, error, attempt)

    def _apply_parameter_completion(self, state, error: Exception):
        """Apply parameter completion recovery strategy."""
        # This would analyze the error to identify missing parameters
        # and add guidance about required parameters
        return state

    def _apply_type_correction(self, state, error: Exception):
        """Apply type correction recovery strategy."""
        # This would provide guidance about correct parameter types
        return state

    def _apply_format_correction(self, state, error: Exception):
        """Apply format correction recovery strategy."""
        # This would provide examples of correct formats
        return state

    def _apply_value_adjustment(self, state, error: Exception):
        """Apply value adjustment recovery strategy."""
        # This would suggest appropriate value ranges
        return state

    def _apply_enum_correction(self, state, error: Exception):
        """Apply enum correction recovery strategy."""
        # This would provide the list of valid choices
        return state

    def _apply_generic_simplification(self, state, error: Exception, attempt: int):
        """Apply generic simplification strategy."""
        # Remove optional parameters, use simpler values
        return state

    def _create_retry_guidance_message(self, error: Exception, strategy: str, attempt: int) -> SystemMessage:
        """
        Create a guidance message to help the agent recover from the error.

        Args:
            error: The error that occurred
            strategy: Recovery strategy being applied
            attempt: Current attempt number

        Returns:
            System message with retry guidance
        """
        error_msg = str(error)

        guidance_templates = {
            'parameter_completion': f"""
Attempt {attempt}/3 - Parameter Error Recovery:
The previous tool call failed due to missing required parameters: {error_msg}

Recovery guidance:
1. Identify all required parameters for the tool
2. Ensure all required parameters are provided with valid values
3. Double-check parameter names for typos
4. Use simpler parameter values if complex ones are failing
""",
            'type_correction': f"""
Attempt {attempt}/3 - Type Error Recovery:
The previous tool call failed due to incorrect parameter types: {error_msg}

Recovery guidance:
1. Check the expected data types for all parameters
2. Convert string numbers to integers/floats where needed
3. Ensure boolean values are true/false, not strings
4. Use proper list/dict formats for complex parameters
""",
            'format_correction': f"""
Attempt {attempt}/3 - Format Error Recovery:
The previous tool call failed due to incorrect parameter format: {error_msg}

Recovery guidance:
1. Check the expected format for parameters (e.g., date formats, email formats)
2. Use standard formats (ISO dates, valid email addresses)
3. Ensure string parameters don't contain invalid characters
4. Verify list and dict parameter structures
""",
            'value_adjustment': f"""
Attempt {attempt}/3 - Value Error Recovery:
The previous tool call failed due to invalid parameter values: {error_msg}

Recovery guidance:
1. Use values within the valid range or set
2. Check minimum/maximum limits for numeric parameters
3. Use reasonable default values for optional parameters
4. Avoid extreme or edge-case values
""",
            'enum_correction': f"""
Attempt {attempt}/3 - Choice Error Recovery:
The previous tool call failed due to invalid parameter choices: {error_msg}

Recovery guidance:
1. Use only the allowed values for choice parameters
2. Check for exact spelling and case sensitivity
3. Review the available options carefully
4. Use the most appropriate choice from the valid set
""",
            'generic_simplification': f"""
Attempt {attempt}/3 - Generic Error Recovery:
The previous tool call failed: {error_msg}

Recovery guidance:
1. Simplify the tool call by removing optional parameters
2. Use basic, safe values for all parameters
3. Double-check all parameter names and values
4. Try a more conservative approach to the task
"""
        }

        guidance = guidance_templates.get(strategy, guidance_templates['generic_simplification'])

        return SystemMessage(
            role="system",
            content=guidance.strip()
        )

    def get_retry_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about retry attempts.

        Returns:
            Dictionary with retry performance metrics
        """
        if not self.retry_sequences:
            return {
                'total_retry_sequences': 0,
                'success_rate': 0.0,
                'average_attempts': 0.0,
                'total_time_spent': 0.0,
                'strategy_effectiveness': {}
            }

        successful_sequences = [seq for seq in self.retry_sequences if seq.final_success]
        total_attempts = sum(len(seq.attempts) for seq in self.retry_sequences)
        total_time = sum(seq.total_duration for seq in self.retry_sequences)

        # Strategy effectiveness analysis
        strategy_stats = {}
        for seq in self.retry_sequences:
            for strategy in seq.recovery_strategies_used:
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {'used': 0, 'successful': 0}
                strategy_stats[strategy]['used'] += 1
                if seq.final_success:
                    strategy_stats[strategy]['successful'] += 1

        # Calculate effectiveness rates
        strategy_effectiveness = {}
        for strategy, stats in strategy_stats.items():
            effectiveness = stats['successful'] / stats['used'] if stats['used'] > 0 else 0
            strategy_effectiveness[strategy] = {
                'success_rate': effectiveness,
                'times_used': stats['used'],
                'successful_recoveries': stats['successful']
            }

        return {
            'total_retry_sequences': len(self.retry_sequences),
            'successful_sequences': len(successful_sequences),
            'success_rate': len(successful_sequences) / len(self.retry_sequences),
            'average_attempts': total_attempts / len(self.retry_sequences),
            'total_time_spent': total_time,
            'strategy_effectiveness': strategy_effectiveness,
            'error_types_encountered': list(set(
                attempt.error_type for seq in self.retry_sequences for attempt in seq.attempts
            ))
        }