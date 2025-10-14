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
from tau2.data_model.message import Message, SystemMessage, UserMessage, ToolMessage
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

        # Track retry attempts per tool call ID to prevent infinite loops
        self.retry_counts: Dict[str, int] = {}  # tool_call_id -> attempt_count
        self.tool_error_history: List[Dict[str, Any]] = []  # Track all tool errors

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

        This method intercepts ToolMessages with errors and adds retry guidance
        to help the LLM recover from validation errors.
        """

        # Check if this is a ToolMessage with an error
        if isinstance(message, ToolMessage):
            if message.error:
                # Check if this error is retryable and hasn't exceeded max retries
                if self._should_retry_tool_error(message, state):
                    state = self._add_retry_guidance_to_state(message, state)

        # Call parent's generate_next_message with potentially modified state
        result = super().generate_next_message(message, state)
        return result

    def _should_retry_tool_error(self, tool_message: ToolMessage, state) -> bool:
        """
        Determine if a tool error should be retried.

        Args:
            tool_message: The ToolMessage with an error
            state: Current conversation state

        Returns:
            True if the error should be retried
        """
        tool_call_id = tool_message.id
        error_content = tool_message.content or ""

        # Check retry count
        current_retry_count = self.retry_counts.get(tool_call_id, 0)
        if current_retry_count >= self.max_retries:
            print(f"[RETRY_AGENT]   Max retries ({self.max_retries}) reached for tool call {tool_call_id}")
            return False

        # Check if error message indicates a retryable error
        error_message = error_content.lower()

        # Common retryable error patterns
        retryable_patterns = [
            'validation', 'parameter', 'argument', 'format',
            'type', 'value', 'range', 'choice', 'required',
            'invalid', 'missing', 'expected', 'error:'
        ]

        is_retryable = any(pattern in error_message for pattern in retryable_patterns)
        return is_retryable

    def _add_retry_guidance_to_state(self, tool_message: ToolMessage, state):
        """
        Add retry guidance to the conversation state to help the LLM recover.

        Args:
            tool_message: The ToolMessage with an error
            state: Current conversation state

        Returns:
            Modified state with retry guidance
        """
        tool_call_id = tool_message.id
        error_content = tool_message.content or ""

        # Increment retry count
        current_retry_count = self.retry_counts.get(tool_call_id, 0)
        self.retry_counts[tool_call_id] = current_retry_count + 1
        attempt_number = self.retry_counts[tool_call_id]

        # Record error in history
        error_record = {
            'tool_call_id': tool_call_id,
            'attempt_number': attempt_number,
            'error_content': error_content,
            'timestamp': time.time()
        }
        self.tool_error_history.append(error_record)

        # Determine recovery strategy based on error content
        recovery_strategy = self._determine_recovery_strategy_from_message(error_content)

        # Create retry guidance message
        guidance_message = self._create_retry_guidance_from_tool_error(
            error_content, recovery_strategy, attempt_number
        )

        # Add guidance to state
        state.messages.append(guidance_message)

        # Log retry attempt
        self.retry_logger.log_tool_execution(
            tool_name=f"retry_guidance_{attempt_number}",
            success=True,
            execution_time=0,
            tool_args={
                "tool_call_id": tool_call_id,
                "error_content": error_content[:200],
                "recovery_strategy": recovery_strategy,
                "attempt": attempt_number
            },
            result={"guidance_added": True}
        )

        return state


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
            print(f"\n[RETRY_AGENT] ───── RETRY ATTEMPT {attempt + 1}/{self.max_retries} ─────")

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
                    strategy_used=f"retry_guidance_{recovery_strategy}",
                    trigger_reason="retry_failure_recovery"
                )

                # Attempt the operation again
                result = super().generate_next_message(message, modified_state)

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

    def _determine_recovery_strategy_from_message(self, error_message: str) -> str:
        """
        Determine the best recovery strategy based on the error message.

        Args:
            error_message: The error message content

        Returns:
            String identifier for the recovery strategy to use
        """
        error_msg_lower = error_message.lower()

        # Check error patterns to classify the error type
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_msg_lower):
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

    def _create_retry_guidance_from_tool_error(self, error_content: str, strategy: str, attempt: int) -> UserMessage:
        """
        Create a guidance message to help the agent recover from a tool error.

        Args:
            error_content: The error message from the ToolMessage
            strategy: Recovery strategy being applied
            attempt: Current attempt number

        Returns:
            User message with retry guidance
        """
        # Extract the actual error message (remove "Error: " prefix if present)
        error_msg = error_content
        if error_msg.startswith("Error: "):
            error_msg = error_msg[7:]

        guidance_templates = {
            'parameter_completion': f"""
🔄 RETRY ATTEMPT {attempt}/3 - Parameter Error Recovery

The tool call failed with: {error_msg}

Recovery guidance:
1. Check if all REQUIRED parameters are provided
2. Review the tool's parameter requirements carefully
3. Ensure parameter names are spelled correctly
4. If a parameter is missing, add it with an appropriate value
5. Try using simpler, more straightforward parameter values

Please retry the tool call with the corrected parameters.
""",
            'type_correction': f"""
🔄 RETRY ATTEMPT {attempt}/3 - Type Error Recovery

The tool call failed with: {error_msg}

Recovery guidance:
1. Check the expected data types for each parameter
2. Convert values to the correct type (e.g., strings to numbers, strings to booleans)
3. Use true/false for boolean values, not "true"/"false" strings
4. Use integers/floats for numeric parameters, not strings
5. Ensure dates are in the correct format (e.g., ISO format)

Please retry the tool call with correctly typed parameters.
""",
            'format_correction': f"""
🔄 RETRY ATTEMPT {attempt}/3 - Format Error Recovery

The tool call failed with: {error_msg}

Recovery guidance:
1. Check the expected format for each parameter (dates, emails, phone numbers, etc.)
2. Use standard formats (ISO 8601 for dates, valid email addresses)
3. Remove any invalid characters from string parameters
4. Verify list and dictionary structures are correct
5. Follow the exact format shown in the tool documentation

Please retry the tool call with correctly formatted parameters.
""",
            'value_adjustment': f"""
🔄 RETRY ATTEMPT {attempt}/3 - Value Error Recovery

The tool call failed with: {error_msg}

Recovery guidance:
1. Use values that are within the valid range or allowed set
2. Check for minimum/maximum limits on numeric parameters
3. Use reasonable, realistic values (avoid extremes or edge cases)
4. If a parameter has constraints, respect them
5. Consider using default or commonly-used values

Please retry the tool call with valid parameter values.
""",
            'enum_correction': f"""
🔄 RETRY ATTEMPT {attempt}/3 - Choice/Enum Error Recovery

The tool call failed with: {error_msg}

Recovery guidance:
1. Use ONLY the allowed values from the predefined set
2. Check for exact spelling and case sensitivity (e.g., "active" vs "ACTIVE")
3. Review the available options in the tool documentation
4. Common mistake: using similar but incorrect values
5. Select the most appropriate choice from the valid options

Please retry the tool call with a valid choice from the allowed values.
""",
            'generic_simplification': f"""
🔄 RETRY ATTEMPT {attempt}/3 - Error Recovery

The tool call failed with: {error_msg}

Recovery guidance:
1. Carefully read the error message to understand what went wrong
2. Simplify the tool call by using basic, straightforward values
3. Remove any optional parameters that might be causing issues
4. Double-check all parameter names and values
5. If unsure, try a more conservative approach

Please retry the tool call with the corrections applied.
Use anotehr tool if necessary, like for calculations or data retrieval.
"""
        }

        guidance = guidance_templates.get(strategy, guidance_templates['generic_simplification'])

        return UserMessage(
            role="user",
            content=guidance.strip()
        )

    def _create_retry_guidance_message(self, error: Exception, strategy: str, attempt: int) -> UserMessage:
        """
        Create a guidance message to help the agent recover from the error.

        Args:
            error: The error that occurred
            strategy: Recovery strategy being applied
            attempt: Current attempt number

        Returns:
            User message with retry guidance (as feedback about the error)
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

        return UserMessage(
            role="user",
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

    def print_retry_summary(self):
        """Print a summary of all retry activity."""
        print(f"\n{'='*80}")
        print(f"[RETRY_AGENT] RETRY STATISTICS SUMMARY")
        print(f"{'='*80}")

        # Print tool error statistics
        if self.tool_error_history:
            print(f"\n[RETRY_AGENT] Tool Error Statistics:")
            print(f"[RETRY_AGENT]   Total tool errors encountered: {len(self.tool_error_history)}")
            print(f"[RETRY_AGENT]   Unique tool calls with errors: {len(self.retry_counts)}")

            # Count retries by tool call
            retry_distribution = {}
            for tool_id, count in self.retry_counts.items():
                retry_distribution[count] = retry_distribution.get(count, 0) + 1

            print(f"[RETRY_AGENT]   Retry distribution:")
            for num_retries in sorted(retry_distribution.keys()):
                count = retry_distribution[num_retries]
                print(f"[RETRY_AGENT]     {num_retries} retries: {count} tool call(s)")

        # Print legacy retry sequence statistics
        if not self.retry_sequences and not self.tool_error_history:
            print(f"[RETRY_AGENT] No retry activity recorded")
            print(f"{'='*80}\n")
            return

        if self.retry_sequences:
            stats = self.get_retry_statistics()

            print(f"\n[RETRY_AGENT] Legacy Retry Sequences:")
            print(f"[RETRY_AGENT]   Total retry sequences: {stats['total_retry_sequences']}")
            print(f"[RETRY_AGENT]   Successful recoveries: {stats['successful_sequences']}")
            print(f"[RETRY_AGENT]   Success rate: {stats['success_rate']:.1%}")
            print(f"[RETRY_AGENT]   Average attempts per sequence: {stats['average_attempts']:.1f}")
            print(f"[RETRY_AGENT]   Total time spent retrying: {stats['total_time_spent']:.2f}s")

            if stats['strategy_effectiveness']:
                print(f"\n[RETRY_AGENT]   Strategy Effectiveness:")
                for strategy, eff in stats['strategy_effectiveness'].items():
                    print(f"[RETRY_AGENT]     {strategy}:")
                    print(f"[RETRY_AGENT]       - Used: {eff['times_used']} times")
                    print(f"[RETRY_AGENT]       - Successful: {eff['successful_recoveries']} times")
                    print(f"[RETRY_AGENT]       - Success rate: {eff['success_rate']:.1%}")

            if stats.get('error_types_encountered'):
                print(f"\n[RETRY_AGENT]   Error types encountered: {', '.join(stats['error_types_encountered'])}")

        print(f"{'='*80}\n")