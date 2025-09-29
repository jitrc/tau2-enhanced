"""
tau2-enhanced: Enhanced logging capabilities for tau2-bench evaluation framework
"""

__version__ = "0.1.0"

# Import domain registration to ensure it happens when the package is imported
from tau2_enhanced.environments.domain_environments import *

# Import enhanced runner components
from .enhanced_runner import EnhancedRunner, run_enhanced_simulation

# Import logging components for direct access
from .logging import (
    ExecutionLogger,
    StateTracker,
    ToolExecutionEvent,
    StateChangeEvent,
    ContextReductionEvent,
    LogLevel
)

# Import enhanced agents
from .agents import (
    RetryManagedLLMAgent,
    ContextManagedLLMAgent,
    EnhancedLLMAgent
)

# Import agent registry functions
from .agents.agent_registry import (
    register_all_enhanced_agents,
    get_enhanced_agents_info,
    get_usage_examples,
    get_performance_expectations,
    print_enhanced_agent_summary
)

__all__ = [
    # Enhanced runner
    'EnhancedRunner',
    'run_enhanced_simulation',

    # Structured logging
    'ExecutionLogger',
    'StateTracker',

    # Event types
    'ToolExecutionEvent',
    'StateChangeEvent',
    'ContextReductionEvent',
    'LogLevel',

    # Enhanced agents
    'RetryManagedLLMAgent',
    'ContextManagedLLMAgent',
    'EnhancedLLMAgent',

    # Agent registry functions
    'register_all_enhanced_agents',
    'get_enhanced_agents_info',
    'get_usage_examples',
    'get_performance_expectations',
    'print_enhanced_agent_summary'
]