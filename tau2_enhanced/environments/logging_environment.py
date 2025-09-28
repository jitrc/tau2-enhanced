import time
from typing import Any, Dict, Optional
from pathlib import Path

from tau2.environment.environment import Environment
from tau2.utils.utils import get_now
from tau2_enhanced.logging import ExecutionLogger, StateTracker


class LoggingEnvironment(Environment):
    """
    Enhanced Environment wrapper with structured event logging.

    This environment wraps the original Environment and adds comprehensive
    logging capabilities using ExecutionLogger and StateTracker.
    """

    def __init__(self, *args, log_file: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize structured loggers
        self.execution_logger = ExecutionLogger(
            log_file=log_file,
            auto_flush=True,
            console_output=False  # Avoid double logging with tau2's logger
        )
        self.state_tracker = StateTracker(
            max_snapshots=1000,
            auto_snapshot=True,
            track_state_hash=True
        )

        # Tracking variables
        self.pre_call_state: dict[str, Any] | None = None
        self._step_counter = 0

    def make_tool_call(self, tool_name: str, requestor="assistant", **kwargs) -> Any:
        """
        Execute a tool call with comprehensive logging.

        This method wraps the original make_tool_call and adds structured
        event logging and state tracking.
        """
        # Increment step counter
        self._step_counter += 1

        # Capture pre-call state
        pre_state_data = self._capture_current_state()
        pre_state_hash = self.get_db_hash()

        # Create pre-execution state snapshot
        self.state_tracker.create_snapshot(
            state_data=pre_state_data,
            action_trigger=f"before_{tool_name}",
            agent_turn=(requestor == "assistant"),
            metadata={
                'tool_name': tool_name,
                'requestor': requestor,
                'step': self._step_counter,
                'args_count': len(kwargs)
            }
        )

        start_time = time.time()
        tool_call_id = f"{tool_name}_{self._step_counter}"

        try:
            # Call the original method
            result = super().make_tool_call(tool_name, requestor, **kwargs)

            # Capture success metrics
            execution_time = time.time() - start_time
            post_state_hash = self.get_db_hash()
            state_changed = pre_state_hash != post_state_hash

            # Log successful tool execution
            self.execution_logger.log_tool_execution(
                tool_name=tool_name,
                success=True,
                execution_time=execution_time,
                tool_args=kwargs,
                result=result,
                requestor=requestor,
                tool_call_id=tool_call_id,
                state_changed=state_changed
            )

            # Handle state changes
            if state_changed:
                # Create post-execution state snapshot
                post_state_data = self._capture_current_state()
                self.state_tracker.create_snapshot(
                    state_data=post_state_data,
                    action_trigger=f"after_{tool_name}",
                    agent_turn=(requestor == "assistant"),
                    metadata={
                        'tool_name': tool_name,
                        'requestor': requestor,
                        'step': self._step_counter,
                        'result_size': len(str(result)) if result else 0
                    }
                )

                # Log state change event
                self.execution_logger.log_state_change(
                    change_summary=f"Tool {tool_name} modified environment state",
                    action_trigger=tool_name,
                    state_type="database",
                    pre_state_hash=pre_state_hash,
                    post_state_hash=post_state_hash,
                    state_diff=self._compute_state_diff(pre_state_hash, post_state_hash)
                )

            return result

        except Exception as e:
            # Capture error details
            execution_time = time.time() - start_time

            # Log failed tool execution
            self.execution_logger.log_tool_execution(
                tool_name=tool_name,
                success=False,
                execution_time=execution_time,
                tool_args=kwargs,
                error_message=str(e),
                error_type=type(e).__name__,
                requestor=requestor,
                tool_call_id=tool_call_id,
                state_changed=False  # Assume no state change on error
            )

            # Re-raise the original exception
            raise

    def _capture_current_state(self) -> Dict[str, Any]:
        """
        Capture current environment state for tracking.

        Returns:
            Dictionary containing current state information
        """
        state_data = {
            'domain_name': self.domain_name,
            'step_counter': self._step_counter,
            'timestamp': time.time()
        }

        # Try to capture database state if available
        try:
            if hasattr(self, 'tools') and self.tools:
                # Try to get database state from tools
                if hasattr(self.tools, 'db'):
                    db = self.tools.db
                    state_data['db_info'] = {
                        'type': type(db).__name__,
                        'hash': self.get_db_hash()
                    }
                    # Add domain-specific state if available
                    if hasattr(db, 'get_state_summary'):
                        state_data['db_summary'] = db.get_state_summary()

        except Exception as e:
            state_data['capture_error'] = str(e)

        return state_data

    def get_enhanced_logs(self) -> Dict[str, Any]:
        """
        Get comprehensive structured logs with all event types and analytics.

        Returns:
            Dictionary containing structured events, snapshots, and performance statistics
        """
        return {
            'execution_events': [event.to_dict() for event in self.execution_logger.events],
            'state_snapshots': [snapshot.to_dict() for snapshot in self.state_tracker.snapshots],
            'statistics': {
                'execution_logger': self.execution_logger.get_statistics(),
                'state_tracker': self.state_tracker.get_statistics()
            },
            'summary': {
                'total_tool_executions': len(self.execution_logger.get_tool_execution_events()),
                'total_state_changes': len(self.execution_logger.get_state_change_events()),
                'total_context_reductions': len(self.execution_logger.get_context_reduction_events()),
                'total_snapshots': len(self.state_tracker.snapshots),
                'steps_completed': self._step_counter
            }
        }

    def export_logs(
        self,
        output_dir: str,
        format: str = "json",
        include_snapshots: bool = True
    ):
        """
        Export all structured logs to files.

        Args:
            output_dir: Directory to save log files
            format: Export format ('json' or 'jsonl')
            include_snapshots: Whether to export state snapshots
        """
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Export execution events
        execution_file = output_path / f"execution_events.{format}"
        self.execution_logger.export_events(execution_file, format=format)

        # Export state snapshots if requested
        if include_snapshots:
            snapshots_file = output_path / f"state_snapshots.{format}"
            self.state_tracker.export_snapshots(snapshots_file, format=format)

        # Export summary
        summary_file = output_path / "summary.json"
        with open(summary_file, 'w') as f:
            import json
            json.dump(self.get_structured_logs()['summary'], f, indent=2)

    def _compute_state_diff(self, pre_state: str | None, post_state: str | None) -> str:
        """
        Compute a human-readable diff between two state hashes.

        Args:
            pre_state: Previous state hash
            post_state: Current state hash

        Returns:
            Human-readable description of the state change
        """
        if pre_state != post_state:
            # In a real scenario, you might decode and compare the DB states
            return "Database state has changed"
        return "No change in database state"

    def __del__(self):
        """Cleanup when environment is destroyed."""
        try:
            # Ensure logs are flushed
            if hasattr(self, 'execution_logger'):
                self.execution_logger.flush()
        except Exception:
            pass  # Ignore cleanup errors
