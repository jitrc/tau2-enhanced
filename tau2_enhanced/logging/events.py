"""
Structured event types for execution logging.

This module defines the structured event classes used throughout the enhanced
logging system. Each event type captures specific information about different
aspects of tau2-bench execution.
"""

import time
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


class LogLevel(Enum):
    """Log levels for execution events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ExecutionEvent:
    """Base class for all execution events."""

    timestamp: float = field(default_factory=time.time)
    level: LogLevel = LogLevel.INFO
    source: str = "unknown"
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'timestamp': self.timestamp,
            'level': self.level.value,
            'source': self.source,
            'message': self.message,
            'metadata': self.metadata,
            'event_type': self.__class__.__name__
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionEvent':
        """Create event from dictionary."""
        # Handle enum conversion
        if 'level' in data and isinstance(data['level'], str):
            data['level'] = LogLevel(data['level'])

        # Remove event_type as it's not a field
        data.pop('event_type', None)

        return cls(**data)


@dataclass
class ToolExecutionEvent(ExecutionEvent):
    """Event for comprehensive tool call execution tracking."""

    # Core tool execution data
    tool_name: str = ""
    tool_args: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    result: Any = None
    result_size: Optional[int] = None
    result_preview: str = ""
    requestor: str = "assistant"
    tool_call_id: str = ""
    validation_errors: List[str] = field(default_factory=list)
    state_changed: bool = False

    # Enhanced argument tracking
    args_count: int = 0
    args_size_bytes: Optional[int] = None
    args_types: Dict[str, str] = field(default_factory=dict)
    args_complexity_score: Optional[float] = None
    has_file_args: bool = False
    has_large_args: bool = False
    sensitive_args_detected: bool = False

    # Function signature and usage tracking
    required_args_provided: List[str] = field(default_factory=list)
    optional_args_provided: List[str] = field(default_factory=list)
    missing_args: List[str] = field(default_factory=list)
    unexpected_args: List[str] = field(default_factory=list)

    # Result analysis
    result_type: Optional[str] = None
    result_complexity_score: Optional[float] = None
    result_contains_errors: bool = False
    result_truncated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        base = super().to_dict()
        base.update({
            # Core execution data
            'tool_name': self.tool_name,
            'tool_args': self.tool_args,
            'execution_time': self.execution_time,
            'success': self.success,
            'error_message': self.error_message,
            'error_type': self.error_type,
            'result_size': self.result_size,
            'result_preview': self.result_preview,
            'requestor': self.requestor,
            'tool_call_id': self.tool_call_id,
            'validation_errors': self.validation_errors,
            'state_changed': self.state_changed,

            # Enhanced argument tracking
            'args_count': self.args_count,
            'args_size_bytes': self.args_size_bytes,
            'args_types': self.args_types,
            'args_complexity_score': self.args_complexity_score,
            'has_file_args': self.has_file_args,
            'has_large_args': self.has_large_args,
            'sensitive_args_detected': self.sensitive_args_detected,

            # Function signature tracking
            'required_args_provided': self.required_args_provided,
            'optional_args_provided': self.optional_args_provided,
            'missing_args': self.missing_args,
            'unexpected_args': self.unexpected_args,

            # Result analysis
            'result_type': self.result_type,
            'result_complexity_score': self.result_complexity_score,
            'result_contains_errors': self.result_contains_errors,
            'result_truncated': self.result_truncated,

            # Don't include full result to avoid huge logs
            'has_result': self.result is not None
        })
        return base

    def __post_init__(self):
        """Post-initialization processing with enhanced argument analysis."""
        if not self.message:
            status = "succeeded" if self.success else "failed"
            self.message = f"Tool {self.tool_name} {status}"

        if not self.source:
            self.source = f"tool:{self.tool_name}"

        # Set log level based on success
        if not self.success:
            self.level = LogLevel.ERROR
        elif self.execution_time and self.execution_time > 5.0:
            self.level = LogLevel.WARNING
        else:
            self.level = LogLevel.INFO

        # Analyze arguments if not already set
        if self.tool_args and not self.args_count:
            self._analyze_arguments()

        # Analyze result if not already set
        if self.result is not None and not self.result_type:
            self._analyze_result()

    def _analyze_arguments(self):
        """Analyze tool arguments for enhanced tracking."""
        if not self.tool_args:
            return

        import json
        import sys
        import re

        # Basic argument metrics
        self.args_count = len(self.tool_args)

        # Calculate argument size
        try:
            args_str = json.dumps(self.tool_args, default=str)
            self.args_size_bytes = len(args_str.encode('utf-8'))
            self.has_large_args = self.args_size_bytes > 1024  # > 1KB
        except Exception:
            self.args_size_bytes = len(str(self.tool_args))
            self.has_large_args = self.args_size_bytes > 1024

        # Analyze argument types
        self.args_types = {
            key: type(value).__name__ for key, value in self.tool_args.items()
        }

        # Calculate complexity score (0-1, higher = more complex)
        complexity_factors = [
            len(self.tool_args) * 0.1,  # Number of args
            sum(1 for v in self.tool_args.values() if isinstance(v, (dict, list))) * 0.2,  # Complex types
            sum(1 for v in self.tool_args.values() if isinstance(v, str) and len(v) > 100) * 0.15,  # Long strings
            (self.args_size_bytes / 1024) * 0.1 if self.args_size_bytes else 0  # Size factor
        ]
        self.args_complexity_score = min(sum(complexity_factors), 1.0)

        # Detect file-related arguments
        file_indicators = ['file', 'path', 'filename', 'document', 'upload', 'attachment']
        self.has_file_args = any(
            any(indicator in str(key).lower() for indicator in file_indicators)
            or any(indicator in str(value).lower() for indicator in file_indicators)
            for key, value in self.tool_args.items()
        )

        # Detect potentially sensitive arguments (basic heuristic)
        sensitive_indicators = ['password', 'key', 'secret', 'token', 'auth', 'credential', 'ssn', 'credit']
        self.sensitive_args_detected = any(
            any(indicator in str(key).lower() for indicator in sensitive_indicators)
            for key in self.tool_args.keys()
        )

    def _analyze_result(self):
        """Analyze result data for enhanced tracking."""
        if self.result is None:
            return

        import json

        # Result type
        self.result_type = type(self.result).__name__

        # Calculate result size if not set
        if not self.result_size:
            try:
                if isinstance(self.result, str):
                    self.result_size = len(self.result)
                else:
                    result_str = json.dumps(self.result, default=str)
                    self.result_size = len(result_str)
            except Exception:
                self.result_size = len(str(self.result))

        # Calculate complexity score
        complexity_factors = []
        if isinstance(self.result, (dict, list)):
            complexity_factors.append(0.3)  # Complex type
            if isinstance(self.result, list):
                complexity_factors.append(len(self.result) * 0.05)  # List length
            elif isinstance(self.result, dict):
                complexity_factors.append(len(self.result) * 0.03)  # Dict keys

        complexity_factors.append((self.result_size / 1024) * 0.1 if self.result_size else 0)
        self.result_complexity_score = min(sum(complexity_factors), 1.0)

        # Check for errors in result
        if isinstance(self.result, str):
            error_indicators = ['error', 'failed', 'exception', 'invalid', 'not found']
            self.result_contains_errors = any(
                indicator in self.result.lower() for indicator in error_indicators
            )

        # Check if result was truncated
        if isinstance(self.result_preview, str) and isinstance(self.result, str):
            self.result_truncated = len(self.result_preview) < len(self.result)


@dataclass
class StateChangeEvent(ExecutionEvent):
    """Event for environment state changes."""

    state_type: str = "unknown"
    previous_state: Any = None
    new_state: Any = None
    change_summary: str = ""
    action_trigger: str = ""
    pre_state_hash: Optional[str] = None
    post_state_hash: Optional[str] = None
    state_diff: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        base = super().to_dict()
        base.update({
            'state_type': self.state_type,
            'change_summary': self.change_summary,
            'action_trigger': self.action_trigger,
            'pre_state_hash': self.pre_state_hash,
            'post_state_hash': self.post_state_hash,
            'state_diff': self.state_diff,
            # Include state snapshots if they're serializable
            'has_previous_state': self.previous_state is not None,
            'has_new_state': self.new_state is not None,
        })
        return base

    def __post_init__(self):
        """Post-initialization processing."""
        if not self.message:
            self.message = f"State changed: {self.change_summary}"

        if not self.source:
            self.source = "environment:state_change"


@dataclass
class ContextReductionEvent(ExecutionEvent):
    """Event for context reduction operations."""

    original_tokens: int = 0
    reduced_tokens: int = 0
    strategy_used: str = ""
    reduction_ratio: float = 1.0
    tokens_saved: int = 0
    warnings: List[str] = field(default_factory=list)
    context_type: str = "conversation"
    trigger_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        base = super().to_dict()
        base.update({
            'original_tokens': self.original_tokens,
            'reduced_tokens': self.reduced_tokens,
            'strategy_used': self.strategy_used,
            'reduction_ratio': self.reduction_ratio,
            'tokens_saved': self.tokens_saved,
            'warnings': self.warnings,
            'context_type': self.context_type,
            'trigger_reason': self.trigger_reason
        })
        return base

    def __post_init__(self):
        """Post-initialization processing."""
        if self.original_tokens and self.reduced_tokens:
            self.reduction_ratio = self.reduced_tokens / self.original_tokens
            self.tokens_saved = self.original_tokens - self.reduced_tokens

        if not self.message:
            self.message = f"Context reduced from {self.original_tokens} to {self.reduced_tokens} tokens"

        if not self.source:
            self.source = "context:reduction"

        # Set log level based on reduction effectiveness
        if self.reduction_ratio > 0.9:
            self.level = LogLevel.WARNING  # Minimal reduction
        elif self.warnings:
            self.level = LogLevel.WARNING
        else:
            self.level = LogLevel.INFO


# Event type mapping for deserialization
EVENT_TYPE_MAP = {
    'ExecutionEvent': ExecutionEvent,
    'ToolExecutionEvent': ToolExecutionEvent,
    'StateChangeEvent': StateChangeEvent,
    'ContextReductionEvent': ContextReductionEvent
}


def event_from_dict(data: Dict[str, Any]) -> ExecutionEvent:
    """Create appropriate event instance from dictionary data."""
    event_type = data.get('event_type', 'ExecutionEvent')
    event_class = EVENT_TYPE_MAP.get(event_type, ExecutionEvent)

    # Create a copy to avoid modifying original data
    event_data = data.copy()

    # Handle enum conversion
    if 'level' in event_data and isinstance(event_data['level'], str):
        event_data['level'] = LogLevel(event_data['level'])

    # Remove fields that don't belong to the dataclass (added by to_dict() but not in constructor)
    extra_fields_to_remove = ['event_type', 'has_result']
    for field in extra_fields_to_remove:
        event_data.pop(field, None)

    try:
        return event_class(**event_data)
    except TypeError as e:
        # If specific event type fails, fall back to base ExecutionEvent
        return ExecutionEvent(
            timestamp=event_data.get('timestamp', time.time()),
            level=event_data.get('level', LogLevel.INFO),
            source=event_data.get('source', 'unknown'),
            message=event_data.get('message', f"Deserialization error: {e}"),
            metadata=event_data
        )