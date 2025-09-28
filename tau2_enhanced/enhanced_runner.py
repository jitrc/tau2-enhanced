"""Enhanced runner that wraps tau2-bench run_tasks with logging capture."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
from loguru import logger

from tau2.data_model.simulation import Results
from tau2.data_model.tasks import Task
from tau2.run import run_tasks
from tau2.registry import registry
from tau2.utils.utils import get_now
from tau2.utils import llm_utils
from tau2.data_model.message import AssistantMessage, ToolCall

from tau2_enhanced.data_model.enhanced_simulation import (
    EnhancedResults,
    EnhancedSimulationRun,
    convert_to_enhanced_results
)
from tau2_enhanced.environments.logging_environment import LoggingEnvironment


def make_enhanced_run_name(
    domain: str,
    agent: str,
    user: str,
    llm_agent: str,
    llm_user: str
) -> str:
    """
    Make a run name using the same pattern as tau2-bench make_run_name.
    """
    clean_llm_agent_name = llm_agent.split("/")[-1]
    agent_name = f"{agent}_{clean_llm_agent_name}"
    clean_llm_user_name = llm_user.split("/")[-1]
    user_name = f"{user}_{clean_llm_user_name}"
    return f"{get_now()}_{domain}_{agent_name}_{user_name}"


class EnhancedRunner:
    """Enhanced runner that captures detailed logging from LoggingEnvironment."""

    def __init__(self, save_dir: Optional[str] = None):
        """
        Initialize enhanced runner.

        Args:
            save_dir: Directory to save enhanced logs. If None, uses current directory + 'enhanced_logs'
        """
        if save_dir is None:
            save_dir = os.path.join(os.getcwd(), 'enhanced_logs')

        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

        # Store environment instances to capture logs later
        self._environment_instances: List[LoggingEnvironment] = []

    def run_tasks_enhanced(
        self,
        domain: str,
        tasks: List[Task],
        agent: str,
        user: str,
        llm_agent: Optional[str] = None,
        llm_args_agent: Optional[Dict] = None,
        llm_user: Optional[str] = None,
        llm_args_user: Optional[Dict] = None,
        num_trials: int = 1,
        max_steps: int = 100,
        max_errors: int = 5,
        max_concurrency: int = 1,
        seed: Optional[int] = None,
        log_level: str = "INFO",
        **kwargs
    ) -> EnhancedResults:
        """
        Run tasks with enhanced logging capture.

        This wraps the original run_tasks and captures enhanced logs from LoggingEnvironments.
        """
        # Clear previous environment instances
        self._environment_instances.clear()

        # Monkey patch the environment creation to capture instances
        original_get_env_constructor = registry.get_env_constructor

        def patched_get_env_constructor(domain_name: str):
            env_constructor = original_get_env_constructor(domain_name)

            def wrapped_constructor(**kwargs):
                env = env_constructor(**kwargs)
                if isinstance(env, LoggingEnvironment):
                    self._environment_instances.append(env)
                return env

            return wrapped_constructor

        # Monkey patch the generate function to handle empty responses
        original_generate = llm_utils.generate

        def patched_generate(model, messages, tools=None, tool_choice=None, **kwargs):
            """
            Patched generate function that handles empty LLM responses gracefully.
            """
            try:
                result = original_generate(model, messages, tools, tool_choice, **kwargs)

                # Check if the result has neither content nor tool calls
                has_content = (result.content is not None and
                             isinstance(result.content, str) and
                             result.content.strip() != "")
                has_tool_calls = result.tool_calls is not None

                if not has_content and not has_tool_calls:
                    logger.warning(f"LLM {model} returned empty response, providing fallback content")
                    # Create a new AssistantMessage with fallback content
                    result = AssistantMessage(
                        role="assistant",
                        content="[Assistant did not provide a response]",
                        tool_calls=None,
                        cost=result.cost,
                        usage=result.usage,
                        raw_data=result.raw_data,
                    )

                return result

            except Exception as e:
                logger.error(f"Error in generate function: {e}")
                raise

        # Apply monkey patches
        registry.get_env_constructor = patched_get_env_constructor
        llm_utils.generate = patched_generate

        try:
            # Run the original tasks
            results: Results = run_tasks(
                domain=domain,
                tasks=tasks,
                agent=agent,
                user=user,
                llm_agent=llm_agent,
                llm_args_agent=llm_args_agent,
                llm_user=llm_user,
                llm_args_user=llm_args_user,
                num_trials=num_trials,
                max_steps=max_steps,
                max_errors=max_errors,
                max_concurrency=max_concurrency,
                seed=seed,
                log_level=log_level,
                **kwargs
            )

        finally:
            # Restore original functions
            registry.get_env_constructor = original_get_env_constructor
            llm_utils.generate = original_generate

        # Convert to enhanced results
        enhanced_results = convert_to_enhanced_results(results)

        # Capture enhanced logs from LoggingEnvironments
        self._capture_enhanced_logs(enhanced_results)

        return enhanced_results

    def _capture_enhanced_logs(self, results: EnhancedResults) -> None:
        """Capture enhanced logs from LoggingEnvironment instances."""
        if not self._environment_instances:
            return

        # For now, we'll aggregate all logs across environments
        # In a more sophisticated setup, you might want to match logs to specific simulations
        all_execution_logs = []
        all_state_snapshots = []

        for env in self._environment_instances:
            if hasattr(env, 'get_enhanced_logs'):
                enhanced_logs = env.get_enhanced_logs()
                all_execution_logs.extend(enhanced_logs.get('execution_logs', []))
                all_state_snapshots.extend(enhanced_logs.get('state_snapshots', []))

        # Apply enhanced logs to simulations
        # For simplicity, we'll apply aggregated logs to all simulations
        # In a production system, you'd want more sophisticated mapping
        for i, sim in enumerate(results.simulations):
            if all_execution_logs or all_state_snapshots:
                sim.execution_logs = all_execution_logs
                sim.state_snapshots = all_state_snapshots
                sim.enhanced_logging_enabled = True

        # Create summary
        if all_execution_logs or all_state_snapshots:
            results.enhanced_logs_summary = {
                'total_execution_logs': len(all_execution_logs),
                'total_state_snapshots': len(all_state_snapshots),
                'environments_with_logs': len([env for env in self._environment_instances if hasattr(env, 'get_enhanced_logs')])
            }

    def save_enhanced_results(
        self,
        results: EnhancedResults,
        domain: str,
        agent: str,
        user: str,
        llm_agent: str,
        llm_user: str,
        save_to: Optional[str] = None
    ) -> tuple[Path, Optional[Path]]:
        """Save enhanced results using tau2-bench naming pattern."""
        if save_to:
            # Use custom filename - save_to should be the base name without extension
            base_path = self.save_dir / save_to
        else:
            # Generate filename using the same pattern as tau2-bench
            run_name = make_enhanced_run_name(domain, agent, user, llm_agent, llm_user)
            base_path = self.save_dir / run_name

        main_path, logs_path = results.save_enhanced(base_path, include_logs=True)
        return main_path, logs_path


# Convenience function for direct usage
def run_enhanced_simulation(
    domain: str,
    tasks: List[Task],
    agent: str = "llm_agent",
    user: str = "user_simulator",
    llm_agent: Optional[str] = None,
    llm_user: Optional[str] = None,
    save_to: Optional[str] = None,
    **kwargs
) -> tuple[EnhancedResults, tuple[Path, Optional[Path]]]:
    """
    Convenience function to run enhanced simulation and save results.

    Args:
        save_to: Custom filename for the results (without extension)

    Returns:
        Tuple of (enhanced_results, (main_path, logs_path))

    Note:
        Results are always saved to 'enhanced_logs' directory in the current working directory.
    """
    # Set defaults for LLM models if not provided
    if llm_agent is None:
        from tau2.config import DEFAULT_LLM_AGENT
        llm_agent = DEFAULT_LLM_AGENT
    if llm_user is None:
        from tau2.config import DEFAULT_LLM_USER
        llm_user = DEFAULT_LLM_USER

    # EnhancedRunner defaults to 'enhanced_logs' directory when save_dir is None
    runner = EnhancedRunner(save_dir=None)
    results = runner.run_tasks_enhanced(
        domain=domain,
        tasks=tasks,
        agent=agent,
        user=user,
        llm_agent=llm_agent,
        llm_user=llm_user,
        **kwargs
    )

    paths = runner.save_enhanced_results(
        results=results,
        domain=domain,
        agent=agent,
        user=user,
        llm_agent=llm_agent,
        llm_user=llm_user,
        save_to=save_to
    )
    return results, paths