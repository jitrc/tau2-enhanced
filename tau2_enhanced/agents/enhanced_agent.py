"""
EnhancedLLMAgent: Combined agent with both retry logic and context management.

This agent combines the capabilities of both RetryManagedLLMAgent and
ContextManagedLLMAgent to provide comprehensive performance optimization,
addressing both the 87% action execution failure rate and the 53% performance
cliff from context pressure.
"""

import time
import copy
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from .retry_agent import RetryManagedLLMAgent, RetrySequence, RetryAttempt
from .context_agent import ContextManagedLLMAgent, ContextReductionResult, TokenUsageStats
from tau2_enhanced.logging import ExecutionLogger


@dataclass
class EnhancedPerformanceMetrics:
    """Combined performance metrics for the enhanced agent."""
    # Context management metrics
    context_reductions: int = 0
    total_tokens_saved: int = 0
    average_information_preservation: float = 0.0

    # Retry mechanism metrics
    retry_sequences: int = 0
    successful_retries: int = 0
    retry_success_rate: float = 0.0

    # Combined effectiveness metrics
    total_operations: int = 0
    operations_with_context_reduction: int = 0
    operations_with_retry: int = 0
    operations_with_both: int = 0

    # Performance impact
    total_context_processing_time: float = 0.0
    total_retry_processing_time: float = 0.0
    net_performance_improvement: float = 0.0


class EnhancedLLMAgent(RetryManagedLLMAgent, ContextManagedLLMAgent):
    """
    Production agent combining retry logic and context management.

    This agent provides the complete solution for tau2-bench performance optimization,
    addressing both validation errors and context length pressure simultaneously.
    """

    def __init__(self, *args, **kwargs):
        # Initialize both parent classes
        # Note: Python's MRO will handle the initialization order
        super().__init__(*args, **kwargs)

        # Combined metrics tracking
        self.combined_metrics = EnhancedPerformanceMetrics()

        # Enhanced logging for combined operations
        self.enhanced_logger = ExecutionLogger(
            log_file=None,  # Will be set by environment if needed
            auto_flush=True,
            console_output=False
        )

        # Operation tracking
        self.operation_counter = 0

    def generate_next_message(self, message, state):
        """
        Override to apply both context reduction and retry logic optimally.

        This method coordinates between context management and retry logic
        to provide maximum performance improvement with minimal overhead.
        """
        self.operation_counter += 1
        operation_start_time = time.time()

        # Step 1: Apply context reduction first (if needed)
        context_reduced = False
        token_stats = self._analyze_token_usage(state.messages)

        if token_stats.is_warning or token_stats.current_tokens > self.context_limit:
            state = self._apply_context_reduction(state, token_stats)
            context_reduced = True
            self.combined_metrics.operations_with_context_reduction += 1

            # Log context reduction
            self.enhanced_logger.log_context_reduction(
                original_tokens=token_stats.current_tokens,
                reduced_tokens=self.estimate_tokens(state.messages),
                reduction_strategy="enhanced_agent_preprocessing",
                information_preserved=True,
                performance_impact=time.time() - operation_start_time
            )

        # Step 2: Attempt message generation with retry logic
        retry_used = False
        try:
            # Try the operation with the (potentially) reduced context
            result = self._generate_with_base_agent(message, state)

        except Exception as e:
            # Check if this is a retryable error
            if self._is_retryable_error(e):
                retry_used = True
                self.combined_metrics.operations_with_retry += 1

                # Apply retry logic on the already-reduced context
                result = self._handle_enhanced_retry_scenario(message, state, e)
            else:
                # Re-raise non-retryable errors
                raise

        # Step 3: Update combined metrics
        operation_time = time.time() - operation_start_time
        self._update_combined_metrics(context_reduced, retry_used, operation_time)

        # Step 4: Log combined operation
        self._log_enhanced_operation(context_reduced, retry_used, operation_time)

        return result

    def _generate_with_base_agent(self, message, state):
        """
        Generate message using the base LLMAgent (bypassing retry logic).

        This allows us to control exactly when retry logic is applied.
        """
        # Call the base LLMAgent directly, not the retry-enabled version
        from tau2.agent.llm_agent import LLMAgent
        return LLMAgent.generate_next_message(self, message, state)

    def _handle_enhanced_retry_scenario(self, message, state, original_error: Exception):
        """
        Handle retry scenario optimized for already-reduced context.

        This version of retry handling is aware that context has already been
        reduced and optimizes the retry strategies accordingly.
        """
        retry_sequence = RetrySequence(
            tool_name="enhanced_operation",
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

                # Determine recovery strategy (enhanced for reduced context)
                recovery_strategy = self._determine_enhanced_recovery_strategy(
                    original_error, state, attempt
                )
                retry_attempt.recovery_strategy = recovery_strategy
                retry_sequence.recovery_strategies_used.append(recovery_strategy)

                # Apply recovery strategy optimized for reduced context
                modified_state = self._apply_enhanced_recovery_strategy(
                    state, original_error, recovery_strategy, attempt
                )

                # Add retry guidance that's aware of context reduction
                retry_guidance = self._create_enhanced_retry_guidance_message(
                    original_error, recovery_strategy, attempt + 1, context_was_reduced=True
                )
                modified_state.messages.append(retry_guidance)

                # Check if we need further context reduction after adding guidance
                guidance_tokens = self.estimate_tokens([retry_guidance])
                total_tokens = self.estimate_tokens(modified_state.messages)

                if total_tokens > self.context_limit * 0.9:  # 90% threshold
                    # Apply additional light reduction to make room for guidance
                    modified_state = self._apply_light_context_reduction_for_retry(modified_state)

                # Attempt the operation again
                result = self._generate_with_base_agent(message, modified_state)

                # Success! Record and return
                retry_attempt.success = True
                retry_sequence.attempts.append(retry_attempt)
                retry_sequence.final_success = True
                retry_sequence.total_duration = time.time() - start_time

                self.retry_sequences.append(retry_sequence)
                self.combined_metrics.successful_retries += 1

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

                    # Re-raise the final error
                    raise

    def _determine_enhanced_recovery_strategy(self, error: Exception, state, attempt: int) -> str:
        """
        Determine recovery strategy optimized for context-reduced state.

        This considers both the error type and the fact that context has
        already been reduced.
        """
        base_strategy = self._determine_recovery_strategy(error)

        # Modify strategy based on context state
        current_tokens = self.estimate_tokens(state.messages)
        token_pressure = current_tokens / self.context_limit

        if token_pressure > 0.8:  # Still high token usage after reduction
            # Use more conservative strategies that add less content
            conservative_strategies = {
                'parameter_completion': 'minimal_parameter_completion',
                'type_correction': 'simple_type_correction',
                'format_correction': 'basic_format_correction',
                'value_adjustment': 'conservative_value_adjustment',
                'enum_correction': 'direct_enum_correction'
            }
            return conservative_strategies.get(base_strategy, 'ultra_minimal_guidance')

        return base_strategy

    def _apply_enhanced_recovery_strategy(self, state, error: Exception, strategy: str, attempt: int):
        """
        Apply recovery strategy optimized for enhanced agent context.
        """
        # Use the base recovery strategy but with context awareness
        modified_state = self._apply_recovery_strategy(state, error, strategy, attempt)

        # Additional optimization: ensure we don't exceed context limits
        if self.estimate_tokens(modified_state.messages) > self.context_limit:
            modified_state = self._apply_light_context_reduction_for_retry(modified_state)

        return modified_state

    def _apply_light_context_reduction_for_retry(self, state):
        """
        Apply minimal context reduction to make room for retry guidance.

        This is a lighter version of context reduction specifically for
        retry scenarios where we need to add guidance messages.
        """
        # Simple compression of verbose messages
        compressed_messages = []
        for msg in state.messages:
            if self._is_verbose_message(msg):
                compressed_msg = self._compress_message_content(msg, compression_level=0.6)
                compressed_messages.append(compressed_msg)
            else:
                compressed_messages.append(msg)

        modified_state = copy.deepcopy(state)
        modified_state.messages = compressed_messages

        return modified_state

    def _create_enhanced_retry_guidance_message(self, error: Exception, strategy: str,
                                              attempt: int, context_was_reduced: bool):
        """
        Create retry guidance message optimized for enhanced agent.
        """
        base_guidance = self._create_retry_guidance_message(error, strategy, attempt)

        # Add context reduction awareness to the guidance
        if context_was_reduced:
            enhanced_content = base_guidance.content + f"""

NOTE: Context has been optimized to focus on recent conversation. If you need
information from earlier in the conversation, use available tools to retrieve
current state information rather than relying on conversation history.
"""
            base_guidance.content = enhanced_content.strip()

        return base_guidance

    def _update_combined_metrics(self, context_reduced: bool, retry_used: bool, operation_time: float):
        """Update combined performance metrics."""
        self.combined_metrics.total_operations += 1

        if context_reduced and retry_used:
            self.combined_metrics.operations_with_both += 1

        if context_reduced:
            # Update context metrics from parent class
            if self.reduction_history:
                latest_reduction = self.reduction_history[-1]
                self.combined_metrics.context_reductions += 1
                self.combined_metrics.total_tokens_saved += (
                    latest_reduction.original_token_count - latest_reduction.reduced_token_count
                )
                self.combined_metrics.total_context_processing_time += latest_reduction.performance_impact

        if retry_used:
            # Update retry metrics from parent class
            self.combined_metrics.retry_sequences += 1
            if self.retry_sequences and self.retry_sequences[-1].final_success:
                self.combined_metrics.successful_retries += 1

        # Update success rate
        if self.combined_metrics.retry_sequences > 0:
            self.combined_metrics.retry_success_rate = (
                self.combined_metrics.successful_retries / self.combined_metrics.retry_sequences
            )

        # Update average information preservation
        if self.reduction_history:
            total_preservation = sum(r.information_preserved for r in self.reduction_history)
            self.combined_metrics.average_information_preservation = (
                total_preservation / len(self.reduction_history)
            )

    def _log_enhanced_operation(self, context_reduced: bool, retry_used: bool, operation_time: float):
        """Log the combined operation for analysis."""
        operation_type = "enhanced_agent_operation"
        if context_reduced and retry_used:
            operation_type = "context_reduction_with_retry"
        elif context_reduced:
            operation_type = "context_reduction_only"
        elif retry_used:
            operation_type = "retry_only"
        else:
            operation_type = "standard_operation"

        self.enhanced_logger.log_tool_execution(
            tool_name=operation_type,
            success=True,
            execution_time=operation_time,
            tool_args={
                "context_reduced": context_reduced,
                "retry_used": retry_used,
                "operation_number": self.operation_counter
            },
            result={
                "enhancement_applied": context_reduced or retry_used,
                "combined_enhancement": context_reduced and retry_used
            }
        )

    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for the enhanced agent.

        Returns:
            Dictionary combining context and retry statistics with enhanced metrics
        """
        # Get base statistics from both parent classes
        context_stats = self.get_context_statistics()
        retry_stats = self.get_retry_statistics()

        # Calculate combined effectiveness metrics
        total_ops = self.combined_metrics.total_operations
        enhancement_usage = {
            'context_only': (self.combined_metrics.operations_with_context_reduction -
                           self.combined_metrics.operations_with_both),
            'retry_only': (self.combined_metrics.operations_with_retry -
                         self.combined_metrics.operations_with_both),
            'both_enhancements': self.combined_metrics.operations_with_both,
            'no_enhancement': (total_ops - self.combined_metrics.operations_with_context_reduction -
                             self.combined_metrics.operations_with_retry +
                             self.combined_metrics.operations_with_both)
        }

        # Calculate overall enhancement impact
        enhancement_rate = (
            (self.combined_metrics.operations_with_context_reduction +
             self.combined_metrics.operations_with_retry -
             self.combined_metrics.operations_with_both) / total_ops
        ) if total_ops > 0 else 0

        return {
            # Combined metrics
            'enhanced_agent_metrics': {
                'total_operations': total_ops,
                'enhancement_usage_rate': enhancement_rate,
                'enhancement_breakdown': enhancement_usage,
                'average_information_preservation': self.combined_metrics.average_information_preservation,
                'total_tokens_saved': self.combined_metrics.total_tokens_saved,
                'successful_retry_rate': self.combined_metrics.retry_success_rate,
                'combined_enhancement_rate': (self.combined_metrics.operations_with_both / total_ops
                                           if total_ops > 0 else 0)
            },

            # Context management metrics
            'context_management': context_stats,

            # Retry mechanism metrics
            'retry_mechanism': retry_stats,

            # Performance analysis
            'performance_analysis': {
                'total_context_processing_time': self.combined_metrics.total_context_processing_time,
                'total_retry_processing_time': sum(seq.total_duration for seq in self.retry_sequences),
                'average_operation_enhancement_overhead': (
                    (self.combined_metrics.total_context_processing_time +
                     sum(seq.total_duration for seq in self.retry_sequences)) / total_ops
                ) if total_ops > 0 else 0,
                'enhancement_efficiency_score': self._calculate_enhancement_efficiency()
            }
        }

    def _calculate_enhancement_efficiency(self) -> float:
        """
        Calculate overall enhancement efficiency score.

        This metric attempts to quantify the net benefit of the enhancements
        relative to their computational cost.
        """
        if self.combined_metrics.total_operations == 0:
            return 0.0

        # Benefits (normalized 0-1)
        context_benefit = min(1.0, self.combined_metrics.total_tokens_saved / 10000)  # Normalize by 10k tokens
        retry_benefit = self.combined_metrics.retry_success_rate

        # Costs (attempt to normalize 0-1)
        context_cost = min(1.0, self.combined_metrics.total_context_processing_time / 10)  # Normalize by 10 seconds
        retry_cost = min(1.0, sum(seq.total_duration for seq in self.retry_sequences) / 30)  # Normalize by 30 seconds

        # Calculate net benefit
        total_benefit = context_benefit + retry_benefit
        total_cost = context_cost + retry_cost

        if total_cost == 0:
            return total_benefit
        else:
            return max(0.0, (total_benefit - total_cost) / (total_benefit + total_cost))

    def configure_enhanced_agent(self,
                               context_limit: int = 6000,
                               warning_threshold: float = 0.8,
                               critical_threshold: float = 0.95,
                               max_retries: int = 3,
                               retry_delay_base: float = 0.5):
        """
        Configure all enhanced agent parameters in one call.

        Args:
            context_limit: Maximum token limit before reduction
            warning_threshold: Start context reduction at this utilization
            critical_threshold: Emergency context reduction threshold
            max_retries: Maximum retry attempts for failed operations
            retry_delay_base: Base delay between retry attempts
        """
        # Configure context management
        self.set_context_limit(context_limit)
        self.set_reduction_thresholds(warning_threshold, critical_threshold)

        # Configure retry mechanism
        self.max_retries = max_retries
        self.retry_delay_base = retry_delay_base

    def reset_enhanced_metrics(self):
        """Reset all enhanced agent metrics and history."""
        self.combined_metrics = EnhancedPerformanceMetrics()
        self.reduction_history.clear()
        self.retry_sequences.clear()
        self.operation_counter = 0