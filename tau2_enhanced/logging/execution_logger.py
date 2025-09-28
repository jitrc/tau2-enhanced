"""
ExecutionLogger for structured event logging with JSONL persistence.

This module provides the ExecutionLogger class that handles structured event
logging with support for multiple event types and persistent storage.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, TextIO, Union
from dataclasses import asdict

from loguru import logger
from .events import (
    ExecutionEvent,
    ToolExecutionEvent,
    StateChangeEvent,
    ContextReductionEvent,
    LogLevel,
    event_from_dict
)


class ExecutionLogger:
    """
    Structured event logger with JSONL persistence and real-time export.

    This logger collects structured events during tau2-bench execution and
    provides various export and analysis capabilities.
    """

    def __init__(
        self,
        log_file: Optional[str] = None,
        auto_flush: bool = True,
        console_output: bool = False,
        buffer_size: int = 100
    ):
        """
        Initialize ExecutionLogger.

        Args:
            log_file: Optional path to JSONL log file for persistent storage
            auto_flush: Whether to flush to file after each event
            console_output: Whether to also log events to console
            buffer_size: Maximum number of events to buffer before forced flush
        """
        self.events: List[ExecutionEvent] = []
        self.log_file = Path(log_file) if log_file else None
        self.auto_flush = auto_flush
        self.console_output = console_output
        self.buffer_size = buffer_size
        self._file_handle: Optional[TextIO] = None
        self._events_since_flush = 0

        # Statistics
        self._start_time = time.time()
        self._event_counts = {
            'total': 0,
            'tool_executions': 0,
            'state_changes': 0,
            'context_reductions': 0,
            'errors': 0
        }

        # Open log file if specified
        if self.log_file:
            self._open_log_file()

    def _open_log_file(self):
        """Open the log file for writing."""
        if self.log_file:
            try:
                # Ensure parent directory exists
                self.log_file.parent.mkdir(parents=True, exist_ok=True)

                # Open in append mode
                self._file_handle = open(self.log_file, 'a', encoding='utf-8')
                logger.debug(f"Opened execution log file: {self.log_file}")
            except Exception as e:
                logger.error(f"Failed to open log file {self.log_file}: {e}")
                self._file_handle = None

    def _close_log_file(self):
        """Close the log file."""
        if self._file_handle:
            try:
                self._file_handle.close()
                self._file_handle = None
                logger.debug(f"Closed execution log file: {self.log_file}")
            except Exception as e:
                logger.error(f"Error closing log file: {e}")

    def log_event(self, event: ExecutionEvent):
        """
        Log a structured execution event.

        Args:
            event: The ExecutionEvent to log
        """
        # Add to memory buffer
        self.events.append(event)

        # Update statistics
        self._event_counts['total'] += 1
        if isinstance(event, ToolExecutionEvent):
            self._event_counts['tool_executions'] += 1
            if not event.success:
                self._event_counts['errors'] += 1
        elif isinstance(event, StateChangeEvent):
            self._event_counts['state_changes'] += 1
        elif isinstance(event, ContextReductionEvent):
            self._event_counts['context_reductions'] += 1

        if event.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self._event_counts['errors'] += 1

        # Console output if enabled
        if self.console_output:
            self._log_to_console(event)

        # Write to file if enabled
        if self._file_handle:
            self._write_event_to_file(event)

        # Auto-flush if needed
        self._events_since_flush += 1
        if self.auto_flush or self._events_since_flush >= self.buffer_size:
            self.flush()

    def _log_to_console(self, event: ExecutionEvent):
        """Log event to console using loguru."""
        level_map = {
            LogLevel.DEBUG: logger.debug,
            LogLevel.INFO: logger.info,
            LogLevel.WARNING: logger.warning,
            LogLevel.ERROR: logger.error,
            LogLevel.CRITICAL: logger.critical
        }

        log_func = level_map.get(event.level, logger.info)
        log_func(f"[{event.source}] {event.message}")

    def _write_event_to_file(self, event: ExecutionEvent):
        """Write a single event to the JSONL file."""
        if self._file_handle:
            try:
                event_dict = event.to_dict()
                json_line = json.dumps(event_dict, default=str) + '\n'
                self._file_handle.write(json_line)
            except Exception as e:
                logger.error(f"Failed to write event to log file: {e}")

    def flush(self):
        """Flush any buffered data to file."""
        if self._file_handle:
            try:
                self._file_handle.flush()
                self._events_since_flush = 0
            except Exception as e:
                logger.error(f"Failed to flush log file: {e}")

    def log_tool_execution(
        self,
        tool_name: str,
        success: bool,
        execution_time: float,
        tool_args: Optional[Dict[str, Any]] = None,
        result: Any = None,
        error_message: Optional[str] = None,
        error_type: Optional[str] = None,
        requestor: str = "assistant",
        tool_call_id: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        state_changed: bool = False
    ):
        """
        Convenience method to log a tool execution event.

        Args:
            tool_name: Name of the tool that was executed
            success: Whether the tool execution succeeded
            execution_time: Time taken to execute the tool (in seconds)
            tool_args: Arguments passed to the tool
            result: Result returned by the tool
            error_message: Error message if execution failed
            error_type: Type of error if execution failed
            requestor: Who requested the tool execution
            tool_call_id: Unique identifier for this tool call
            validation_errors: List of validation errors
            state_changed: Whether the tool call changed the environment state
        """
        # Generate tool_call_id if not provided
        if tool_call_id is None:
            tool_call_id = f"{tool_name}_{len(self.events)}"

        # Generate result preview
        result_preview = ""
        result_size = None
        if result is not None:
            result_str = str(result)
            result_preview = result_str[:200]
            result_size = len(result_str)

        event = ToolExecutionEvent(
            tool_name=tool_name,
            tool_args=tool_args or {},
            execution_time=execution_time,
            success=success,
            error_message=error_message,
            error_type=error_type,
            result=result,
            result_size=result_size,
            result_preview=result_preview,
            requestor=requestor,
            tool_call_id=tool_call_id,
            validation_errors=validation_errors or [],
            state_changed=state_changed
        )

        self.log_event(event)

    def log_state_change(
        self,
        change_summary: str,
        action_trigger: str,
        state_type: str = "database",
        pre_state_hash: Optional[str] = None,
        post_state_hash: Optional[str] = None,
        state_diff: str = ""
    ):
        """
        Convenience method to log a state change event.

        Args:
            change_summary: Brief description of what changed
            action_trigger: What action triggered the state change
            state_type: Type of state that changed
            pre_state_hash: Hash/snapshot of state before change
            post_state_hash: Hash/snapshot of state after change
            state_diff: Detailed description of the differences
        """
        event = StateChangeEvent(
            state_type=state_type,
            change_summary=change_summary,
            action_trigger=action_trigger,
            pre_state_hash=pre_state_hash,
            post_state_hash=post_state_hash,
            state_diff=state_diff
        )

        self.log_event(event)

    def log_context_reduction(
        self,
        original_tokens: int,
        reduced_tokens: int,
        strategy_used: str,
        trigger_reason: str = "",
        warnings: Optional[List[str]] = None,
        context_type: str = "conversation"
    ):
        """
        Convenience method to log a context reduction event.

        Args:
            original_tokens: Number of tokens before reduction
            reduced_tokens: Number of tokens after reduction
            strategy_used: Strategy used for reduction
            trigger_reason: Why the reduction was triggered
            warnings: Any warnings during reduction
            context_type: Type of context being reduced
        """
        event = ContextReductionEvent(
            original_tokens=original_tokens,
            reduced_tokens=reduced_tokens,
            strategy_used=strategy_used,
            trigger_reason=trigger_reason,
            warnings=warnings or [],
            context_type=context_type
        )

        self.log_event(event)

    def log_error(
        self,
        message: str,
        error: Exception,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Convenience method to log an error event.

        Args:
            message: Error message
            error: Exception object
            source: Source of the error
            metadata: Additional metadata about the error
        """
        event = ExecutionEvent(
            level=LogLevel.ERROR,
            source=source,
            message=f"{message}: {str(error)}",
            metadata={
                **(metadata or {}),
                'exception_type': type(error).__name__,
                'exception_message': str(error)
            }
        )

        self.log_event(event)

    def get_events_by_type(self, event_type: type) -> List[ExecutionEvent]:
        """Get all events of a specific type."""
        return [event for event in self.events if isinstance(event, event_type)]

    def get_tool_execution_events(self) -> List[ToolExecutionEvent]:
        """Get all tool execution events."""
        return self.get_events_by_type(ToolExecutionEvent)

    def get_state_change_events(self) -> List[StateChangeEvent]:
        """Get all state change events."""
        return self.get_events_by_type(StateChangeEvent)

    def get_context_reduction_events(self) -> List[ContextReductionEvent]:
        """Get all context reduction events."""
        return self.get_events_by_type(ContextReductionEvent)

    def get_events_in_time_range(
        self,
        start_time: float,
        end_time: float
    ) -> List[ExecutionEvent]:
        """Get events within a specific time range."""
        return [
            event for event in self.events
            if start_time <= event.timestamp <= end_time
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        current_time = time.time()
        duration = current_time - self._start_time

        return {
            'duration_seconds': duration,
            'events_per_second': self._event_counts['total'] / duration if duration > 0 else 0,
            'total_events': len(self.events),
            'event_counts': self._event_counts.copy(),
            'memory_events': len(self.events),
            'log_file': str(self.log_file) if self.log_file else None,
            'auto_flush': self.auto_flush,
            'events_since_flush': self._events_since_flush
        }

    def export_events(
        self,
        output_file: Union[str, Path],
        event_types: Optional[List[type]] = None,
        time_range: Optional[tuple[float, float]] = None,
        format: str = "json"
    ):
        """
        Export events to a file.

        Args:
            output_file: Path to output file
            event_types: Optional list of event types to export
            time_range: Optional (start_time, end_time) tuple to filter events
            format: Export format ('json', 'jsonl', or 'csv')
        """
        # Filter events
        events_to_export = self.events

        if event_types:
            events_to_export = [
                event for event in events_to_export
                if any(isinstance(event, event_type) for event_type in event_types)
            ]

        if time_range:
            start_time, end_time = time_range
            events_to_export = [
                event for event in events_to_export
                if start_time <= event.timestamp <= end_time
            ]

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if format.lower() == 'json':
                self._export_json(events_to_export, output_path)
            elif format.lower() == 'jsonl':
                self._export_jsonl(events_to_export, output_path)
            elif format.lower() == 'csv':
                self._export_csv(events_to_export, output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")

            logger.info(f"Exported {len(events_to_export)} events to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export events: {e}")
            raise

    def _export_json(self, events: List[ExecutionEvent], output_path: Path):
        """Export events as a single JSON array."""
        with open(output_path, 'w', encoding='utf-8') as f:
            event_dicts = [event.to_dict() for event in events]
            json.dump({
                'events': event_dicts,
                'metadata': {
                    'export_timestamp': time.time(),
                    'total_events': len(event_dicts),
                    'statistics': self.get_statistics()
                }
            }, f, indent=2, default=str)

    def _export_jsonl(self, events: List[ExecutionEvent], output_path: Path):
        """Export events as JSONL (one JSON object per line)."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for event in events:
                event_dict = event.to_dict()
                json_line = json.dumps(event_dict, default=str) + '\n'
                f.write(json_line)

    def _export_csv(self, events: List[ExecutionEvent], output_path: Path):
        """Export events as CSV."""
        import pandas as pd

        # Convert events to flat dictionaries
        event_dicts = []
        for event in events:
            event_dict = event.to_dict()
            # Flatten metadata
            metadata = event_dict.pop('metadata', {})
            for key, value in metadata.items():
                event_dict[f'metadata_{key}'] = value
            event_dicts.append(event_dict)

        df = pd.DataFrame(event_dicts)
        df.to_csv(output_path, index=False)

    def load_events_from_file(self, input_file: Union[str, Path]):
        """
        Load events from a JSONL or JSON file.

        Args:
            input_file: Path to input file
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Log file not found: {input_path}")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                if input_path.suffix == '.json':
                    # JSON format
                    data = json.load(f)
                    if isinstance(data, dict) and 'events' in data:
                        event_dicts = data['events']
                    else:
                        event_dicts = data if isinstance(data, list) else [data]
                else:
                    # JSONL format
                    event_dicts = []
                    for line in f:
                        if line.strip():
                            event_dicts.append(json.loads(line))

            # Convert dictionaries to event objects
            loaded_events = []
            for event_dict in event_dicts:
                try:
                    event = event_from_dict(event_dict)
                    loaded_events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to deserialize event: {e}")
                    continue

            # Add to current events
            self.events.extend(loaded_events)
            logger.info(f"Loaded {len(loaded_events)} events from {input_path}")

        except Exception as e:
            logger.error(f"Failed to load events from {input_path}: {e}")
            raise

    def clear_events(self):
        """Clear all events from memory."""
        self.events.clear()
        self._events_since_flush = 0
        logger.debug("Cleared all events from ExecutionLogger")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.flush()
        self._close_log_file()

    def __del__(self):
        """Destructor to ensure file is closed."""
        self._close_log_file()