"""
EnhancedLLMAgent: Combined agent with both retry logic and context management.

This agent combines the capabilities of both RetryManagedLLMAgent and
ContextManagedLLMAgent to provide comprehensive performance optimization,
addressing both the 87% action execution failure rate and the 53% performance
cliff from context pressure.

SIMPLIFIED IMPLEMENTATION:
Uses Python's MRO (Method Resolution Order) to naturally compose the behaviors:
1. RetryManagedLLMAgent intercepts ToolMessages with errors
2. Calls super().generate_next_message() which goes to ContextManagedLLMAgent
3. ContextManagedLLMAgent applies context reduction when needed
4. Both behaviors work together without manual coordination
"""

from typing import Any, Dict

from .retry_agent import RetryManagedLLMAgent
from .context_agent import ContextManagedLLMAgent


class EnhancedLLMAgent(RetryManagedLLMAgent, ContextManagedLLMAgent):
    """
    Production agent combining retry logic and context management.

    This agent provides the complete solution for tau2-bench performance optimization,
    addressing both validation errors and context length pressure simultaneously.

    Method Resolution Order (MRO):
    EnhancedLLMAgent → RetryManagedLLMAgent → ContextManagedLLMAgent → LLMAgent

    This means:
    1. generate_next_message() first goes to RetryManagedLLMAgent
    2. RetryManagedLLMAgent intercepts ToolMessages with errors
    3. It calls super().generate_next_message() → ContextManagedLLMAgent
    4. ContextManagedLLMAgent applies context reduction if needed
    5. It calls super().generate_next_message() → LLMAgent
    6. LLMAgent calls the LLM API

    The behaviors compose naturally without manual coordination!
    """

    def __init__(self, *args, use_simplified_context: bool = True, **kwargs):
        # Initialize both parent classes via MRO
        # This will call RetryManagedLLMAgent.__init__ first, then ContextManagedLLMAgent.__init__
        super().__init__(*args, use_simplified_context=use_simplified_context, **kwargs)

    # NOTE: We DO NOT override generate_next_message()!
    # Let the parent classes handle it through MRO:
    # 1. RetryManagedLLMAgent.generate_next_message() - handles tool errors
    # 2. ContextManagedLLMAgent.generate_next_message() - handles context reduction
    # 3. LLMAgent.generate_next_message() - calls LLM API

    # The parent classes coordinate automatically through super() calls!

    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for the enhanced agent.

        Returns:
            Dictionary combining context and retry statistics
        """
        # Get base statistics from both parent classes
        context_stats = self.get_context_statistics()
        retry_stats = self.get_retry_statistics()

        return {
            # Context management metrics
            'context_management': context_stats,

            # Retry mechanism metrics
            'retry_mechanism': retry_stats,

            # Summary
            'summary': {
                'total_context_reductions': context_stats.get('total_reductions', 0),
                'total_retry_sequences': len(self.retry_sequences) if hasattr(self, 'retry_sequences') else 0,
                'total_tool_errors': len(self.tool_error_history) if hasattr(self, 'tool_error_history') else 0,
                'unique_retried_calls': len(self.retry_counts) if hasattr(self, 'retry_counts') else 0,
            }
        }

    def print_enhanced_summary(self):
        """Print a combined summary of both retry and context management."""
        print(f"\n{'='*80}")
        print(f"[ENHANCED_AGENT] COMBINED STATISTICS SUMMARY")
        print(f"{'='*80}\n")

        # Print retry statistics
        print(f"--- RETRY MECHANISM ---")
        if hasattr(self, 'print_retry_summary'):
            self.print_retry_summary()
        else:
            print(f"[ENHANCED_AGENT] No retry activity\n")

        # Print context statistics
        print(f"\n--- CONTEXT MANAGEMENT ---")
        if hasattr(self, 'print_context_summary'):
            self.print_context_summary()
        else:
            print(f"[ENHANCED_AGENT] No context management activity\n")

        print(f"{'='*80}\n")

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
        if hasattr(self, 'reduction_history'):
            self.reduction_history.clear()
        if hasattr(self, 'retry_sequences'):
            self.retry_sequences.clear()
        if hasattr(self, 'retry_counts'):
            self.retry_counts.clear()
        if hasattr(self, 'tool_error_history'):
            self.tool_error_history.clear()