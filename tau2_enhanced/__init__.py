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
    'LogLevel'
]