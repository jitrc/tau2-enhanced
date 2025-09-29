"""
ContextManagedLLMAgent: Agent with intelligent context length management.

This agent extends the base LLMAgent to handle context length pressure through
sliding window reduction and token optimization, addressing the 53% performance
cliff at 3,000+ tokens identified in the tau2-bench analysis.
"""

import time
import copy
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Warning: tiktoken not available. Using approximate token counting.")

from tau2.agent.llm_agent import LLMAgent
from tau2.data_model.message import Message, SystemMessage, UserMessage, AssistantMessage
from tau2_enhanced.logging import ExecutionLogger


@dataclass
class ContextReductionResult:
    """Results of a context reduction operation."""
    original_token_count: int
    reduced_token_count: int
    original_message_count: int
    reduced_message_count: int
    reduction_strategy: str
    information_preserved: float  # 0-1 score
    performance_impact: float  # seconds
    messages_dropped: int
    bytes_saved: int


@dataclass
class TokenUsageStats:
    """Token usage statistics for monitoring."""
    current_tokens: int
    limit_tokens: int
    utilization: float  # 0-1
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95

    @property
    def is_warning(self) -> bool:
        return self.utilization >= self.warning_threshold

    @property
    def is_critical(self) -> bool:
        return self.utilization >= self.critical_threshold


class ContextManagedLLMAgent(LLMAgent):
    """
    Agent with intelligent context length management.

    This agent automatically applies context reduction strategies when
    the conversation approaches token limits, maintaining performance
    while preserving essential information.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Context management configuration
        self.context_limit = 6000  # Conservative limit for Grok-3 and similar models
        self.warning_threshold = 0.8  # Start reduction at 80% of limit
        self.critical_threshold = 0.95  # Emergency reduction at 95%
        self.min_context_reserve = 500  # Reserve tokens for response generation

        # Token estimation
        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.tokenizer = None
                print("Warning: Could not initialize tiktoken encoder. Using approximation.")
        else:
            self.tokenizer = None

        # Context reduction history
        self.reduction_history: List[ContextReductionResult] = []

        # Initialize context logger
        self.context_logger = ExecutionLogger(
            log_file=None,  # Will be set by environment if needed
            auto_flush=True,
            console_output=False
        )

    def generate_next_message(self, message, state):
        """
        Override to apply context reduction before LLM call when needed.

        This method checks token usage and applies appropriate reduction
        strategies to keep the conversation within optimal token limits.
        """
        # Analyze current token usage
        token_stats = self._analyze_token_usage(state.messages)

        # Log token usage for monitoring
        self.context_logger.log_context_reduction(
            original_tokens=token_stats.current_tokens,
            reduced_tokens=token_stats.current_tokens,  # No reduction yet
            strategy_used="token_analysis",
            trigger_reason="performance_monitoring"
        )

        # Apply context reduction if needed
        if token_stats.is_warning or token_stats.current_tokens > self.context_limit:
            reduced_state = self._apply_context_reduction(state, token_stats)
            return super().generate_next_message(message, reduced_state)
        else:
            return super().generate_next_message(message, state)

    def _analyze_token_usage(self, messages: List[Message]) -> TokenUsageStats:
        """
        Analyze current token usage in the conversation.

        Args:
            messages: List of conversation messages

        Returns:
            Token usage statistics
        """
        current_tokens = self.estimate_tokens(messages)
        utilization = current_tokens / self.context_limit

        return TokenUsageStats(
            current_tokens=current_tokens,
            limit_tokens=self.context_limit,
            utilization=utilization,
            warning_threshold=self.warning_threshold,
            critical_threshold=self.critical_threshold
        )

    def estimate_tokens(self, messages: List[Message]) -> int:
        """
        Estimate token count for a list of messages.

        Args:
            messages: List of messages to count

        Returns:
            Estimated token count
        """
        if self.tokenizer:
            return self._tiktoken_estimate(messages)
        else:
            return self._approximate_estimate(messages)

    def _tiktoken_estimate(self, messages: List[Message]) -> int:
        """Use tiktoken for accurate token counting."""
        total_tokens = 0

        for msg in messages:
            # Count content tokens
            if hasattr(msg, 'content') and msg.content:
                total_tokens += len(self.tokenizer.encode(msg.content))

            # Count tool call tokens
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if hasattr(tool_call, 'arguments'):
                        total_tokens += len(self.tokenizer.encode(str(tool_call.arguments)))

            # Add overhead for message structure (role, metadata, etc.)
            total_tokens += 10  # Estimated overhead per message

        return total_tokens

    def _approximate_estimate(self, messages: List[Message]) -> int:
        """Use approximate token counting when tiktoken is unavailable."""
        total_chars = 0

        for msg in messages:
            # Count content characters
            if hasattr(msg, 'content') and msg.content:
                total_chars += len(msg.content)

            # Count tool call characters
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if hasattr(tool_call, 'arguments'):
                        total_chars += len(str(tool_call.arguments))

        # Approximate: 4 characters per token (varies by language/content)
        return int(total_chars / 4) + len(messages) * 10  # +10 tokens per message overhead

    def _apply_context_reduction(self, state, token_stats: TokenUsageStats):
        """
        Apply context reduction strategies based on current token usage.

        Args:
            state: Current conversation state
            token_stats: Token usage analysis

        Returns:
            Modified state with reduced context
        """
        start_time = time.time()
        original_messages = state.messages.copy()

        # Choose reduction strategy based on severity
        if token_stats.is_critical:
            # Emergency reduction - aggressive strategies
            reduced_messages = self._emergency_context_reduction(original_messages)
            strategy = "emergency_reduction"
        elif token_stats.is_warning:
            # Warning level - moderate reduction
            reduced_messages = self._moderate_context_reduction(original_messages)
            strategy = "moderate_reduction"
        else:
            # Preventive reduction
            reduced_messages = self._preventive_context_reduction(original_messages)
            strategy = "preventive_reduction"

        # Create modified state
        modified_state = copy.deepcopy(state)
        modified_state.messages = reduced_messages

        # Calculate reduction metrics
        processing_time = time.time() - start_time
        original_tokens = self.estimate_tokens(original_messages)
        reduced_tokens = self.estimate_tokens(reduced_messages)

        # Calculate information preservation score
        information_preserved = self._calculate_information_preservation(
            original_messages, reduced_messages
        )

        # Calculate bytes saved
        original_bytes = sum(len(str(msg.content) if hasattr(msg, 'content') else str(msg))
                           for msg in original_messages)
        reduced_bytes = sum(len(str(msg.content) if hasattr(msg, 'content') else str(msg))
                          for msg in reduced_messages)

        # Record reduction result
        reduction_result = ContextReductionResult(
            original_token_count=original_tokens,
            reduced_token_count=reduced_tokens,
            original_message_count=len(original_messages),
            reduced_message_count=len(reduced_messages),
            reduction_strategy=strategy,
            information_preserved=information_preserved,
            performance_impact=processing_time,
            messages_dropped=len(original_messages) - len(reduced_messages),
            bytes_saved=original_bytes - reduced_bytes
        )

        self.reduction_history.append(reduction_result)

        # Log the context reduction
        self.context_logger.log_context_reduction(
            original_tokens=original_tokens,
            reduced_tokens=reduced_tokens,
            strategy_used=strategy,
            trigger_reason="context_limit_exceeded"
        )

        # Log significant reductions
        if original_tokens > reduced_tokens + 100:
            print(f"Context reduced: {original_tokens} → {reduced_tokens} tokens "
                  f"({len(original_messages)} → {len(reduced_messages)} messages) "
                  f"using {strategy}")

        return modified_state

    def _emergency_context_reduction(self, messages: List[Message]) -> List[Message]:
        """
        Apply aggressive context reduction for critical token usage.

        Strategy: Keep only system messages + last few messages + compress everything
        """
        # Step 1: Separate message types
        system_messages = [msg for msg in messages if isinstance(msg, SystemMessage)]
        other_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]

        # Step 2: Keep only the most recent messages
        keep_recent = min(5, len(other_messages))  # Keep last 5 messages
        recent_messages = other_messages[-keep_recent:] if keep_recent > 0 else []

        # Step 3: Compress tool calls in recent messages
        compressed_messages = []
        for msg in recent_messages:
            compressed_msg = self._compress_message_content(msg, compression_level=0.3)
            compressed_messages.append(compressed_msg)

        # Step 4: Create summary of dropped conversation
        if len(other_messages) > keep_recent:
            dropped_count = len(other_messages) - keep_recent
            summary_msg = SystemMessage(
                role="system",
                content=f"Previous conversation summary: {dropped_count} messages were "
                       f"compressed due to context limit. Recent {keep_recent} messages "
                       f"retained for immediate context."
            )
            return system_messages + [summary_msg] + compressed_messages
        else:
            return system_messages + compressed_messages

    def _moderate_context_reduction(self, messages: List[Message]) -> List[Message]:
        """
        Apply moderate context reduction for warning-level token usage.

        Strategy: Sliding window + selective compression
        """
        # Separate message types
        system_messages = [msg for msg in messages if isinstance(msg, SystemMessage)]
        other_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]

        # Calculate how many messages to keep
        system_tokens = self.estimate_tokens(system_messages)
        available_tokens = self.context_limit - system_tokens - self.min_context_reserve

        # Keep recent messages that fit in available tokens
        kept_messages = []
        token_budget = available_tokens

        for msg in reversed(other_messages):
            msg_tokens = self.estimate_tokens([msg])

            # Try compressed version if original is too large
            if msg_tokens > token_budget and token_budget > 100:
                compressed_msg = self._compress_message_content(msg, compression_level=0.6)
                compressed_tokens = self.estimate_tokens([compressed_msg])

                if compressed_tokens <= token_budget:
                    kept_messages.insert(0, compressed_msg)
                    token_budget -= compressed_tokens
                else:
                    break  # Can't fit even compressed version

            elif msg_tokens <= token_budget:
                kept_messages.insert(0, msg)
                token_budget -= msg_tokens
            else:
                break  # Message too large to fit

        # Add summary if we dropped messages
        if len(kept_messages) < len(other_messages):
            dropped_count = len(other_messages) - len(kept_messages)
            summary_msg = SystemMessage(
                role="system",
                content=f"Context optimized: {dropped_count} earlier messages "
                       f"compressed to maintain recent conversation context."
            )
            return system_messages + [summary_msg] + kept_messages
        else:
            return system_messages + kept_messages

    def _preventive_context_reduction(self, messages: List[Message]) -> List[Message]:
        """
        Apply light context reduction for preventive optimization.

        Strategy: Compress verbose messages while keeping all messages
        """
        optimized_messages = []

        for msg in messages:
            # Light compression for verbose messages
            if self._is_verbose_message(msg):
                compressed_msg = self._compress_message_content(msg, compression_level=0.8)
                optimized_messages.append(compressed_msg)
            else:
                optimized_messages.append(msg)

        return optimized_messages

    def _is_verbose_message(self, message: Message) -> bool:
        """Check if a message is verbose and suitable for compression."""
        if not hasattr(message, 'content') or not message.content:
            return False

        content_length = len(message.content)

        # Consider messages verbose if they're very long
        return content_length > 1000

    def _compress_message_content(self, message: Message, compression_level: float = 0.7) -> Message:
        """
        Compress message content while preserving key information.

        Args:
            message: Message to compress
            compression_level: Target compression level (0-1, higher = less compression)

        Returns:
            Message with compressed content
        """
        if not hasattr(message, 'content') or not message.content:
            return message

        original_content = message.content
        target_length = int(len(original_content) * compression_level)

        # Create compressed version
        if len(original_content) <= target_length:
            return message  # No compression needed

        # For tool responses, preserve key information
        if 'error' in original_content.lower():
            # Keep error messages more detailed
            compressed_content = original_content[:target_length] + " [error details truncated]"
        elif any(keyword in original_content.lower() for keyword in ['success', 'completed', 'done']):
            # Compress successful operations more aggressively
            compressed_content = original_content[:target_length//2] + " [operation successful, details truncated]"
        else:
            # General compression
            compressed_content = original_content[:target_length] + " [content truncated]"

        # Create new message with compressed content
        new_message = copy.deepcopy(message)
        new_message.content = compressed_content

        return new_message

    def _calculate_information_preservation(self, original_messages: List[Message],
                                          reduced_messages: List[Message]) -> float:
        """
        Calculate how much information was preserved during reduction.

        Args:
            original_messages: Original message list
            reduced_messages: Reduced message list

        Returns:
            Information preservation score (0-1)
        """
        # Simple heuristic based on message count and content preservation
        message_preservation = len(reduced_messages) / len(original_messages) if original_messages else 1.0

        # Calculate content preservation
        original_content_length = sum(
            len(msg.content) if hasattr(msg, 'content') and msg.content else 0
            for msg in original_messages
        )
        reduced_content_length = sum(
            len(msg.content) if hasattr(msg, 'content') and msg.content else 0
            for msg in reduced_messages
        )

        content_preservation = (reduced_content_length / original_content_length
                              if original_content_length > 0 else 1.0)

        # Weighted average (favor content preservation)
        return 0.3 * message_preservation + 0.7 * content_preservation

    def get_context_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about context management.

        Returns:
            Dictionary with context reduction performance metrics
        """
        if not self.reduction_history:
            return {
                'total_reductions': 0,
                'average_token_savings': 0,
                'average_information_preservation': 0,
                'total_processing_time': 0,
                'strategy_usage': {}
            }

        # Calculate aggregate statistics
        total_reductions = len(self.reduction_history)
        token_savings = [r.original_token_count - r.reduced_token_count for r in self.reduction_history]
        avg_token_savings = sum(token_savings) / len(token_savings)

        information_scores = [r.information_preserved for r in self.reduction_history]
        avg_information_preservation = sum(information_scores) / len(information_scores)

        total_processing_time = sum(r.performance_impact for r in self.reduction_history)

        # Strategy usage analysis
        strategy_usage = {}
        for result in self.reduction_history:
            strategy = result.reduction_strategy
            if strategy not in strategy_usage:
                strategy_usage[strategy] = {
                    'count': 0,
                    'average_token_savings': 0,
                    'average_information_preservation': 0
                }

            strategy_usage[strategy]['count'] += 1
            strategy_usage[strategy]['average_token_savings'] += (
                result.original_token_count - result.reduced_token_count
            )
            strategy_usage[strategy]['average_information_preservation'] += result.information_preserved

        # Calculate averages for each strategy
        for strategy_stats in strategy_usage.values():
            if strategy_stats['count'] > 0:
                strategy_stats['average_token_savings'] /= strategy_stats['count']
                strategy_stats['average_information_preservation'] /= strategy_stats['count']

        return {
            'total_reductions': total_reductions,
            'average_token_savings': avg_token_savings,
            'average_information_preservation': avg_information_preservation,
            'total_processing_time': total_processing_time,
            'strategy_usage': strategy_usage,
            'max_token_savings': max(token_savings) if token_savings else 0,
            'total_messages_dropped': sum(r.messages_dropped for r in self.reduction_history),
            'total_bytes_saved': sum(r.bytes_saved for r in self.reduction_history)
        }

    def set_context_limit(self, limit: int):
        """
        Update the context limit for this agent.

        Args:
            limit: New context limit in tokens
        """
        self.context_limit = limit

    def set_reduction_thresholds(self, warning: float = 0.8, critical: float = 0.95):
        """
        Update the reduction thresholds.

        Args:
            warning: Warning threshold (0-1)
            critical: Critical threshold (0-1)
        """
        self.warning_threshold = warning
        self.critical_threshold = critical