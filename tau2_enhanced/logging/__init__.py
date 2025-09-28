"""
Enhanced logging system for tau2-bench with structured event logging.

This package provides structured event logging capabilities including:
- ToolExecutionEvent: Tool call tracking with timing and success/failure
- StateChangeEvent: Environment state change tracking
- ContextReductionEvent: Context management and reduction tracking
- ExecutionLogger: Structured event logging with JSONL persistence
- StateTracker: Environment state snapshots and diff tracking
"""

from .events import (
    LogLevel,
    ExecutionEvent,
    ToolExecutionEvent,
    StateChangeEvent,
    ContextReductionEvent
)
from .execution_logger import ExecutionLogger
from .state_tracker import StateTracker, StateSnapshot

__all__ = [
    # Event types
    'LogLevel',
    'ExecutionEvent',
    'ToolExecutionEvent',
    'StateChangeEvent',
    'ContextReductionEvent',

    # Loggers
    'ExecutionLogger',
    'StateTracker',
    'StateSnapshot'
]