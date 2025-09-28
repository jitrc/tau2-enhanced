import time
from typing import Any, Dict

from tau2.environment.environment import Environment
from tau2.utils.utils import get_now


class LoggingEnvironment(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execution_logs: list[dict[str, Any]] = []
        self.state_snapshots: list[dict[str, Any]] = []
        self.pre_call_state: dict[str, Any] | None = None

    def make_tool_call(self, tool_name: str, requestor="assistant", **kwargs) -> Any:
        # Capture pre-call state
        pre_state = self.get_db_hash()  # or more detailed state capture
        self.pre_call_state = {
            'timestamp': get_now(),
            'tool_name': tool_name,
            'requestor': requestor,
            'arguments': kwargs,
            'pre_state_hash': pre_state
        }

        start_time = time.time()

        try:
            # Call the original method
            result = super().make_tool_call(tool_name, requestor, **kwargs)

            # Capture success metrics
            execution_time = time.time() - start_time
            post_state = self.get_db_hash()

            self.execution_logs.append({
                'tool_call_id': f"{tool_name}_{len(self.execution_logs)}",
                'validation_errors': [],  # Could capture if validation layer exposed
                'execution_time': execution_time,
                'success': True,
                'result_preview': str(result)[:200],
                'state_changed': pre_state != post_state
            })

            if pre_state != post_state:
                self.state_snapshots.append({
                    'timestamp': get_now(),
                    'action_before': tool_name,
                    'pre_state_hash': pre_state,
                    'post_state_hash': post_state,
                    'state_diff': self._compute_state_diff(pre_state, post_state)
                })

            return result

        except Exception as e:
            # Capture error details
            execution_time = time.time() - start_time

            self.execution_logs.append({
                'tool_call_id': f"{tool_name}_{len(self.execution_logs)}",
                'validation_errors': [str(e)],
                'execution_time': execution_time,
                'success': False,
                'error_details': str(e),
                'error_type': type(e).__name__
            })

            raise  # Re-raise the original exception

    def get_enhanced_logs(self) -> Dict[str, Any]:
        return {
            'execution_logs': self.execution_logs,
            'state_snapshots': self.state_snapshots
        }

    def _compute_state_diff(self, pre_state: str | None, post_state: str | None) -> str:
        if pre_state != post_state:
            # In a real scenario, you might decode and compare the DB states
            return "Database state has changed."
        return "No change in database state."
