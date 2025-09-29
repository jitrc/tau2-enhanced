"""
Tests for enhanced agent registry functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from tau2_enhanced.agents.agent_registry import (
    EnhancedAgentRegistry,
    register_all_enhanced_agents,
    get_enhanced_agents_info,
    get_usage_examples,
    get_performance_expectations
)
from tau2_enhanced.agents import RetryManagedLLMAgent, ContextManagedLLMAgent, EnhancedLLMAgent


class TestEnhancedAgentRegistry:
    """Test suite for EnhancedAgentRegistry."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = EnhancedAgentRegistry()

    @patch('tau2_enhanced.agents.agent_registry.registry')
    def test_register_single_agent_success(self, mock_tau2_registry):
        """Test successful registration of a single agent."""
        mock_tau2_registry.get_agents.return_value = {}
        mock_tau2_registry.register_agent.return_value = None

        result = self.registry.register_enhanced_agent(
            'test_agent',
            RetryManagedLLMAgent,
            'Test agent description'
        )

        assert result is True
        mock_tau2_registry.register_agent.assert_called_once_with(RetryManagedLLMAgent, 'test_agent')

        # Check that agent info was stored
        agent_info = self.registry.get_agent_info('test_agent')
        assert agent_info is not None
        assert agent_info['class_name'] == 'RetryManagedLLMAgent'
        assert agent_info['description'] == 'Test agent description'
        assert agent_info['registered'] is True

    @patch('tau2_enhanced.agents.agent_registry.registry')
    def test_register_single_agent_already_exists(self, mock_tau2_registry):
        """Test registration when agent already exists."""
        mock_tau2_registry.get_agents.return_value = {'test_agent': 'existing'}

        result = self.registry.register_enhanced_agent(
            'test_agent',
            RetryManagedLLMAgent,
            'Test agent description'
        )

        assert result is True
        mock_tau2_registry.register_agent.assert_not_called()

    @patch('tau2_enhanced.agents.agent_registry.registry')
    def test_register_single_agent_failure(self, mock_tau2_registry):
        """Test registration failure handling."""
        mock_tau2_registry.get_agents.return_value = {}
        mock_tau2_registry.register_agent.side_effect = Exception("Registration failed")

        result = self.registry.register_enhanced_agent(
            'test_agent',
            RetryManagedLLMAgent,
            'Test agent description'
        )

        assert result is False

        # Check that error was recorded
        agent_info = self.registry.get_agent_info('test_agent')
        assert agent_info is not None
        assert agent_info['registered'] is False
        assert 'error' in agent_info

    @patch('tau2_enhanced.agents.agent_registry.registry')
    def test_register_all_agents_success(self, mock_tau2_registry):
        """Test successful registration of all enhanced agents."""
        mock_tau2_registry.get_agents.return_value = {}
        mock_tau2_registry.register_agent.return_value = None

        result = self.registry.register_all_enhanced_agents()

        assert len(result) == 3  # Should register 3 agents
        assert 'retry_agent' in result
        assert 'context_agent' in result
        assert 'enhanced_agent' in result

        # Check that tau2 registry was called for each agent
        assert mock_tau2_registry.register_agent.call_count == 3

    def test_get_registered_agents_empty(self):
        """Test getting registered agents when none are registered."""
        agents = self.registry.get_registered_agents()
        assert agents == {}

    def test_is_enhanced_agent(self):
        """Test enhanced agent detection."""
        # Initially no agents
        assert not self.registry.is_enhanced_agent('test_agent')

        # Add agent info
        self.registry._registered_agents['test_agent'] = {
            'class_name': 'TestAgent',
            'registered': True
        }

        assert self.registry.is_enhanced_agent('test_agent')
        assert not self.registry.is_enhanced_agent('other_agent')

    def test_get_agent_info(self):
        """Test getting agent information."""
        # Non-existent agent
        assert self.registry.get_agent_info('nonexistent') is None

        # Add agent info
        agent_info = {
            'class_name': 'TestAgent',
            'description': 'Test description',
            'registered': True
        }
        self.registry._registered_agents['test_agent'] = agent_info

        retrieved_info = self.registry.get_agent_info('test_agent')
        assert retrieved_info == agent_info

    def test_get_usage_examples(self):
        """Test getting usage examples."""
        # No registered agents
        examples = self.registry.get_usage_examples()
        assert 'comparison' not in examples

        # Add some registered agents
        self.registry._registered_agents['retry_agent'] = {'registered': True}
        self.registry._registered_agents['context_agent'] = {'registered': True}

        examples = self.registry.get_usage_examples()
        assert 'retry_agent' in examples
        assert 'context_agent' in examples
        assert 'comparison' in examples

        # Check example format
        assert '--agent retry_agent' in examples['retry_agent']
        assert 'retry_agent,context_agent,llm_agent' in examples['comparison']

    def test_get_performance_expectations(self):
        """Test getting performance expectations."""
        expectations = self.registry.get_performance_expectations()

        assert 'retry_agent' in expectations
        assert 'context_agent' in expectations
        assert 'enhanced_agent' in expectations

        # Check structure
        for agent_id, expectation in expectations.items():
            assert 'addresses' in expectation
            assert 'expected_improvement' in expectation
            assert 'primary_benefit' in expectation
            assert 'overhead' in expectation


class TestRegistryFunctions:
    """Test the convenience functions for agent registry."""

    @patch('tau2_enhanced.agents.agent_registry.enhanced_agent_registry')
    def test_register_all_enhanced_agents_function(self, mock_registry):
        """Test the register_all_enhanced_agents convenience function."""
        mock_registry.register_all_enhanced_agents.return_value = {'test': 'result'}

        result = register_all_enhanced_agents()

        assert result == {'test': 'result'}
        mock_registry.register_all_enhanced_agents.assert_called_once()

    @patch('tau2_enhanced.agents.agent_registry.enhanced_agent_registry')
    def test_get_enhanced_agents_info_function(self, mock_registry):
        """Test the get_enhanced_agents_info convenience function."""
        mock_registry.get_registered_agents.return_value = {'test': 'info'}

        result = get_enhanced_agents_info()

        assert result == {'test': 'info'}
        mock_registry.get_registered_agents.assert_called_once()

    @patch('tau2_enhanced.agents.agent_registry.enhanced_agent_registry')
    def test_get_usage_examples_function(self, mock_registry):
        """Test the get_usage_examples convenience function."""
        mock_registry.get_usage_examples.return_value = {'test': 'example'}

        result = get_usage_examples()

        assert result == {'test': 'example'}
        mock_registry.get_usage_examples.assert_called_once()

    @patch('tau2_enhanced.agents.agent_registry.enhanced_agent_registry')
    def test_get_performance_expectations_function(self, mock_registry):
        """Test the get_performance_expectations convenience function."""
        mock_registry.get_performance_expectations.return_value = {'test': 'expectation'}

        result = get_performance_expectations()

        assert result == {'test': 'expectation'}
        mock_registry.get_performance_expectations.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])