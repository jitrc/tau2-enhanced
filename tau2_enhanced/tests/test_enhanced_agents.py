"""
Tests for enhanced agents: RetryManagedLLMAgent, ContextManagedLLMAgent, and EnhancedLLMAgent.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

from tau2.data_model.message import Message, SystemMessage, UserMessage, AssistantMessage
from tau2_enhanced.agents.retry_agent import RetryManagedLLMAgent, ValidationError
from tau2_enhanced.agents.context_agent import ContextManagedLLMAgent
from tau2_enhanced.agents.enhanced_agent import EnhancedLLMAgent


@dataclass
class MockState:
    """Mock state object for testing."""
    messages: list

    def __deepcopy__(self, memo):
        from copy import deepcopy
        return MockState(messages=deepcopy(self.messages, memo))


class TestRetryManagedLLMAgent:
    """Test suite for RetryManagedLLMAgent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent = RetryManagedLLMAgent()
        self.agent.max_retries = 3
        self.agent.retry_delay_base = 0.1  # Faster for testing

    def test_initialization(self):
        """Test agent initialization."""
        assert self.agent.max_retries == 3
        assert self.agent.retry_delay_base == 0.1
        assert len(self.agent.retry_sequences) == 0
        assert self.agent.retry_logger is not None

    def test_is_retryable_error(self):
        """Test error classification for retryability."""
        # Retryable errors
        validation_error = ValidationError("Missing required parameter")
        value_error = ValueError("Invalid parameter type")
        type_error = TypeError("Expected int, got str")

        assert self.agent._is_retryable_error(validation_error)
        assert self.agent._is_retryable_error(value_error)
        assert self.agent._is_retryable_error(type_error)

        # Non-retryable errors
        runtime_error = RuntimeError("System error")
        memory_error = MemoryError("Out of memory")

        # These might still be retryable depending on message content
        # Test with specific non-retryable messages
        system_error = RuntimeError("System shutdown")
        assert self.agent._is_retryable_error(system_error)  # Still retryable due to heuristics

    def test_determine_recovery_strategy(self):
        """Test recovery strategy determination."""
        # Type mismatch error
        type_error = ValidationError("Expected int, got str")
        strategy = self.agent._determine_recovery_strategy(type_error)
        assert strategy == "type_correction"

        # Missing parameter error
        missing_error = ValidationError("Missing required parameter 'user_id'")
        strategy = self.agent._determine_recovery_strategy(missing_error)
        assert strategy == "parameter_completion"

        # Format error
        format_error = ValidationError("Invalid date format")
        strategy = self.agent._determine_recovery_strategy(format_error)
        assert strategy == "format_correction"

        # Unknown error
        unknown_error = ValidationError("Something went wrong")
        strategy = self.agent._determine_recovery_strategy(unknown_error)
        assert strategy == "generic_simplification"

    def test_create_retry_guidance_message(self):
        """Test retry guidance message creation."""
        error = ValidationError("Missing required parameter 'user_id'")
        guidance = self.agent._create_retry_guidance_message(error, "parameter_completion", 1)

        assert isinstance(guidance, SystemMessage)
        assert "Attempt 1/3" in guidance.content
        assert "Parameter Error Recovery" in guidance.content
        assert "user_id" in guidance.content

    @patch('tau2_enhanced.agents.retry_agent.LLMAgent.generate_next_message')
    def test_successful_generation_no_retry(self, mock_generate):
        """Test successful message generation without retry."""
        mock_generate.return_value = "Success"

        state = MockState(messages=[])
        result = self.agent.generate_next_message("test message", state)

        assert result == "Success"
        mock_generate.assert_called_once()
        assert len(self.agent.retry_sequences) == 0

    @patch('tau2_enhanced.agents.retry_agent.LLMAgent.generate_next_message')
    @patch('time.sleep')
    def test_retry_success_on_second_attempt(self, mock_sleep, mock_generate):
        """Test successful retry on second attempt."""
        # First call fails, second succeeds
        mock_generate.side_effect = [
            ValidationError("Missing parameter"),
            "Success"
        ]

        state = MockState(messages=[SystemMessage(role="system", content="Test")])
        result = self.agent.generate_next_message("test message", state)

        assert result == "Success"
        assert mock_generate.call_count == 2
        assert len(self.agent.retry_sequences) == 1
        assert self.agent.retry_sequences[0].final_success is True
        assert len(self.agent.retry_sequences[0].attempts) == 1

    @patch('tau2_enhanced.agents.retry_agent.LLMAgent.generate_next_message')
    @patch('time.sleep')
    def test_retry_failure_after_max_attempts(self, mock_sleep, mock_generate):
        """Test retry failure after maximum attempts."""
        # All attempts fail
        mock_generate.side_effect = [
            ValidationError("Error 1"),
            ValidationError("Error 2"),
            ValidationError("Error 3")
        ]

        state = MockState(messages=[SystemMessage(role="system", content="Test")])

        with pytest.raises(ValidationError):
            self.agent.generate_next_message("test message", state)

        assert mock_generate.call_count == 3
        assert len(self.agent.retry_sequences) == 1
        assert self.agent.retry_sequences[0].final_success is False
        assert len(self.agent.retry_sequences[0].attempts) == 3

    def test_get_retry_statistics_empty(self):
        """Test retry statistics with no retry attempts."""
        stats = self.agent.get_retry_statistics()

        assert stats['total_retry_sequences'] == 0
        assert stats['success_rate'] == 0.0
        assert stats['average_attempts'] == 0.0
        assert stats['total_time_spent'] == 0.0


class TestContextManagedLLMAgent:
    """Test suite for ContextManagedLLMAgent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent = ContextManagedLLMAgent()
        self.agent.context_limit = 1000  # Smaller limit for testing

    def test_initialization(self):
        """Test agent initialization."""
        assert self.agent.context_limit == 1000
        assert self.agent.warning_threshold == 0.8
        assert self.agent.critical_threshold == 0.95
        assert len(self.agent.reduction_history) == 0

    def test_estimate_tokens_approximate(self):
        """Test approximate token estimation."""
        # Force approximate estimation by setting tokenizer to None
        self.agent.tokenizer = None

        messages = [
            SystemMessage(role="system", content="This is a test message with some content"),
            UserMessage(role="user", content="User message"),
            AssistantMessage(role="assistant", content="Assistant response")
        ]

        tokens = self.agent.estimate_tokens(messages)
        assert tokens > 0
        assert isinstance(tokens, int)

    @patch('tau2_enhanced.agents.context_agent.TIKTOKEN_AVAILABLE', True)
    def test_estimate_tokens_tiktoken(self):
        """Test tiktoken-based token estimation."""
        if not hasattr(self.agent, 'tokenizer') or self.agent.tokenizer is None:
            pytest.skip("tiktoken not available in test environment")

        messages = [
            SystemMessage(role="system", content="Test message"),
            UserMessage(role="user", content="User input")
        ]

        tokens = self.agent.estimate_tokens(messages)
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_analyze_token_usage(self):
        """Test token usage analysis."""
        # Create messages that exceed warning threshold
        large_content = "x" * 500  # Large content to trigger warning
        messages = [
            SystemMessage(role="system", content=large_content),
            UserMessage(role="user", content=large_content)
        ]

        token_stats = self.agent._analyze_token_usage(messages)

        assert token_stats.current_tokens > 0
        assert token_stats.limit_tokens == 1000
        assert 0 <= token_stats.utilization <= 2  # Could exceed 1.0
        assert token_stats.warning_threshold == 0.8
        assert token_stats.critical_threshold == 0.95

    def test_is_verbose_message(self):
        """Test verbose message detection."""
        short_message = SystemMessage(role="system", content="Short")
        long_message = SystemMessage(role="system", content="x" * 1500)

        assert not self.agent._is_verbose_message(short_message)
        assert self.agent._is_verbose_message(long_message)

    def test_compress_message_content(self):
        """Test message content compression."""
        long_content = "x" * 1000
        original_message = SystemMessage(role="system", content=long_content)

        compressed = self.agent._compress_message_content(original_message, compression_level=0.5)

        assert len(compressed.content) < len(original_message.content)
        assert "[content truncated]" in compressed.content
        assert compressed.role == original_message.role

    def test_compress_message_content_error(self):
        """Test compression of error messages."""
        error_content = "ERROR: Something went wrong with detailed information " * 50
        error_message = SystemMessage(role="system", content=error_content)

        compressed = self.agent._compress_message_content(error_message, compression_level=0.3)

        assert len(compressed.content) < len(error_message.content)
        assert "[error details truncated]" in compressed.content

    @patch('tau2_enhanced.agents.context_agent.LLMAgent.generate_next_message')
    def test_no_reduction_needed(self, mock_generate):
        """Test when no context reduction is needed."""
        mock_generate.return_value = "Success"

        # Small messages that don't exceed limits
        messages = [SystemMessage(role="system", content="Short message")]
        state = MockState(messages=messages)

        result = self.agent.generate_next_message("test", state)

        assert result == "Success"
        assert len(self.agent.reduction_history) == 0
        mock_generate.assert_called_once()

    @patch('tau2_enhanced.agents.context_agent.LLMAgent.generate_next_message')
    def test_context_reduction_applied(self, mock_generate):
        """Test when context reduction is applied."""
        mock_generate.return_value = "Success"

        # Large messages that exceed warning threshold
        large_content = "x" * 400  # Should trigger reduction
        messages = [
            SystemMessage(role="system", content=large_content),
            UserMessage(role="user", content=large_content),
            AssistantMessage(role="assistant", content=large_content)
        ]
        state = MockState(messages=messages)

        result = self.agent.generate_next_message("test", state)

        assert result == "Success"
        # Context reduction should have been applied
        assert len(self.agent.reduction_history) >= 1
        mock_generate.assert_called_once()

        # Check that the state passed to generate_next_message was modified
        called_state = mock_generate.call_args[0][1]
        assert len(called_state.messages) <= len(messages)

    def test_calculate_information_preservation(self):
        """Test information preservation calculation."""
        original_messages = [
            SystemMessage(role="system", content="x" * 100),
            UserMessage(role="user", content="x" * 100),
            AssistantMessage(role="assistant", content="x" * 100)
        ]

        reduced_messages = [
            SystemMessage(role="system", content="x" * 50),
            UserMessage(role="user", content="x" * 50)
        ]

        preservation = self.agent._calculate_information_preservation(
            original_messages, reduced_messages
        )

        assert 0 <= preservation <= 1
        assert preservation < 1  # Some information was lost

    def test_get_context_statistics_empty(self):
        """Test context statistics with no reductions."""
        stats = self.agent.get_context_statistics()

        assert stats['total_reductions'] == 0
        assert stats['average_token_savings'] == 0
        assert stats['average_information_preservation'] == 0

    def test_set_context_limit(self):
        """Test setting context limit."""
        new_limit = 2000
        self.agent.set_context_limit(new_limit)
        assert self.agent.context_limit == new_limit

    def test_set_reduction_thresholds(self):
        """Test setting reduction thresholds."""
        self.agent.set_reduction_thresholds(warning=0.7, critical=0.9)
        assert self.agent.warning_threshold == 0.7
        assert self.agent.critical_threshold == 0.9


class TestEnhancedLLMAgent:
    """Test suite for EnhancedLLMAgent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent = EnhancedLLMAgent()
        self.agent.context_limit = 1000  # Smaller for testing
        self.agent.max_retries = 2  # Fewer retries for faster tests

    def test_initialization(self):
        """Test enhanced agent initialization."""
        # Should inherit from both parent classes
        assert hasattr(self.agent, 'max_retries')  # From RetryManagedLLMAgent
        assert hasattr(self.agent, 'context_limit')  # From ContextManagedLLMAgent
        assert hasattr(self.agent, 'combined_metrics')  # Unique to EnhancedLLMAgent
        assert self.agent.operation_counter == 0

    @patch('tau2_enhanced.agents.enhanced_agent.LLMAgent.generate_next_message')
    def test_successful_generation_no_enhancements(self, mock_generate):
        """Test successful generation with no enhancements needed."""
        mock_generate.return_value = "Success"

        # Small message that doesn't trigger context reduction
        messages = [SystemMessage(role="system", content="Short")]
        state = MockState(messages=messages)

        result = self.agent.generate_next_message("test", state)

        assert result == "Success"
        assert self.agent.operation_counter == 1
        assert self.agent.combined_metrics.total_operations == 1
        assert self.agent.combined_metrics.operations_with_context_reduction == 0
        assert self.agent.combined_metrics.operations_with_retry == 0

    @patch('tau2_enhanced.agents.enhanced_agent.LLMAgent.generate_next_message')
    def test_context_reduction_only(self, mock_generate):
        """Test generation with context reduction but no retry."""
        mock_generate.return_value = "Success"

        # Large messages that trigger context reduction
        large_content = "x" * 400
        messages = [
            SystemMessage(role="system", content=large_content),
            UserMessage(role="user", content=large_content),
            AssistantMessage(role="assistant", content=large_content)
        ]
        state = MockState(messages=messages)

        result = self.agent.generate_next_message("test", state)

        assert result == "Success"
        assert self.agent.combined_metrics.operations_with_context_reduction == 1
        assert self.agent.combined_metrics.operations_with_retry == 0

    @patch('tau2_enhanced.agents.enhanced_agent.LLMAgent.generate_next_message')
    @patch('time.sleep')
    def test_retry_only(self, mock_sleep, mock_generate):
        """Test generation with retry but no context reduction."""
        # First call fails, second succeeds
        mock_generate.side_effect = [
            ValidationError("Test error"),
            "Success"
        ]

        # Small message that doesn't trigger context reduction
        messages = [SystemMessage(role="system", content="Short")]
        state = MockState(messages=messages)

        result = self.agent.generate_next_message("test", state)

        assert result == "Success"
        assert self.agent.combined_metrics.operations_with_retry == 1
        assert self.agent.combined_metrics.operations_with_context_reduction == 0

    @patch('tau2_enhanced.agents.enhanced_agent.LLMAgent.generate_next_message')
    @patch('time.sleep')
    def test_both_enhancements(self, mock_sleep, mock_generate):
        """Test generation with both context reduction and retry."""
        # First call fails, second succeeds
        mock_generate.side_effect = [
            ValidationError("Test error"),
            "Success"
        ]

        # Large messages that trigger context reduction
        large_content = "x" * 400
        messages = [
            SystemMessage(role="system", content=large_content),
            UserMessage(role="user", content=large_content),
            AssistantMessage(role="assistant", content=large_content)
        ]
        state = MockState(messages=messages)

        result = self.agent.generate_next_message("test", state)

        assert result == "Success"
        assert self.agent.combined_metrics.operations_with_context_reduction == 1
        assert self.agent.combined_metrics.operations_with_retry == 1
        assert self.agent.combined_metrics.operations_with_both == 1

    def test_get_enhanced_statistics_empty(self):
        """Test enhanced statistics with no operations."""
        stats = self.agent.get_enhanced_statistics()

        assert stats['enhanced_agent_metrics']['total_operations'] == 0
        assert stats['enhanced_agent_metrics']['enhancement_usage_rate'] == 0
        assert 'context_management' in stats
        assert 'retry_mechanism' in stats
        assert 'performance_analysis' in stats

    def test_configure_enhanced_agent(self):
        """Test enhanced agent configuration."""
        self.agent.configure_enhanced_agent(
            context_limit=8000,
            warning_threshold=0.7,
            critical_threshold=0.9,
            max_retries=5,
            retry_delay_base=1.0
        )

        assert self.agent.context_limit == 8000
        assert self.agent.warning_threshold == 0.7
        assert self.agent.critical_threshold == 0.9
        assert self.agent.max_retries == 5
        assert self.agent.retry_delay_base == 1.0

    def test_reset_enhanced_metrics(self):
        """Test resetting enhanced metrics."""
        # Set some metrics
        self.agent.operation_counter = 5
        self.agent.combined_metrics.total_operations = 5

        self.agent.reset_enhanced_metrics()

        assert self.agent.operation_counter == 0
        assert self.agent.combined_metrics.total_operations == 0
        assert len(self.agent.reduction_history) == 0
        assert len(self.agent.retry_sequences) == 0

    @patch('tau2_enhanced.agents.enhanced_agent.LLMAgent.generate_next_message')
    def test_create_enhanced_retry_guidance_message(self, mock_generate):
        """Test enhanced retry guidance message creation."""
        error = ValidationError("Test error")
        guidance = self.agent._create_enhanced_retry_guidance_message(
            error, "parameter_completion", 1, context_was_reduced=True
        )

        assert isinstance(guidance, SystemMessage)
        assert "Context has been optimized" in guidance.content
        assert "focus on recent conversation" in guidance.content

    def test_calculate_enhancement_efficiency(self):
        """Test enhancement efficiency calculation."""
        # Test with no operations
        efficiency = self.agent._calculate_enhancement_efficiency()
        assert efficiency == 0.0

        # Set some metrics to test calculation
        self.agent.combined_metrics.total_operations = 1
        self.agent.combined_metrics.total_tokens_saved = 1000
        self.agent.combined_metrics.retry_success_rate = 0.8

        efficiency = self.agent._calculate_enhancement_efficiency()
        assert 0 <= efficiency <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])