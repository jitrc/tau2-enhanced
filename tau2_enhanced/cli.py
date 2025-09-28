"""
Enhanced CLI interface that wraps tau2-bench CLI with enhanced logging capabilities.
"""

import sys
import argparse
import os
import json
from pathlib import Path
from typing import Optional, List

from tau2.run import get_options
from tau2.config import *
from tau2_enhanced import run_enhanced_simulation


def create_enhanced_parser():
    """Create argument parser for enhanced tau2 CLI."""
    parser = argparse.ArgumentParser(description="tau2-enhanced: Enhanced tau2-bench with detailed logging")

    # Get available options
    options = get_options()

    # Domain arguments
    parser.add_argument(
        "--domain", "-d",
        type=str,
        choices=options.domains + ["airline_enhanced"],  # Add our enhanced domains
        required=True,
        help="The domain to run the simulation on"
    )

    # Task selection
    parser.add_argument(
        "--task-set-name",
        type=str,
        choices=options.task_sets + ["airline_enhanced"],  # Add our enhanced task sets
        help="The task set to run the simulation on. If not provided, will load default task set for the domain."
    )
    parser.add_argument(
        "--task-ids",
        type=str,
        nargs='+',
        help="Specific task IDs to run"
    )
    parser.add_argument(
        "--num-tasks",
        type=int,
        help="Number of tasks to run"
    )

    # Agent configuration
    parser.add_argument(
        "--agent",
        type=str,
        default=DEFAULT_AGENT_IMPLEMENTATION,
        choices=options.agents,
        help=f"The agent implementation to use. Default is {DEFAULT_AGENT_IMPLEMENTATION}."
    )
    parser.add_argument(
        "--agent-llm",
        type=str,
        default=DEFAULT_LLM_AGENT,
        help=f"The LLM to use for the agent. Default is {DEFAULT_LLM_AGENT}."
    )
    parser.add_argument(
        "--agent-llm-args",
        type=str,
        default='{"temperature": 0.0}',
        help='The arguments to pass to the LLM for the agent. Default is \'{"temperature": 0.0}\'.'
    )

    # User configuration
    parser.add_argument(
        "--user",
        type=str,
        default=DEFAULT_USER_IMPLEMENTATION,
        choices=options.users,
        help=f"The user implementation to use. Default is {DEFAULT_USER_IMPLEMENTATION}."
    )
    parser.add_argument(
        "--user-llm",
        type=str,
        default=DEFAULT_LLM_USER,
        help=f"The LLM to use for the user. Default is {DEFAULT_LLM_USER}."
    )
    parser.add_argument(
        "--user-llm-args",
        type=str,
        default='{"temperature": 0.0}',
        help='The arguments to pass to the LLM for the user. Default is \'{"temperature": 0.0}\'.'
    )

    # Simulation parameters
    parser.add_argument(
        "--num-trials",
        type=int,
        default=DEFAULT_NUM_TRIALS,
        help="The number of times each task is run. Default is 1."
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=DEFAULT_MAX_STEPS,
        help=f"Maximum number of steps per simulation. Default is {DEFAULT_MAX_STEPS}."
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=DEFAULT_MAX_ERRORS,
        help=f"Maximum number of errors allowed. Default is {DEFAULT_MAX_ERRORS}."
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=DEFAULT_MAX_CONCURRENCY,
        help=f"Maximum number of concurrent simulations. Default is {DEFAULT_MAX_CONCURRENCY}."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for reproducibility."
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=DEFAULT_LOG_LEVEL,
        help=f"Logging level. Default is {DEFAULT_LOG_LEVEL}."
    )
    parser.add_argument(
        "--save-to",
        type=str,
        help="Custom save directory name for results"
    )

    return parser


def enhanced_main(cli_args: Optional[List[str]] = None):
    """
    Enhanced main function that parses CLI arguments and runs with enhanced logging.

    Args:
        cli_args: List of CLI arguments (if None, uses sys.argv[1:])
    """
    if cli_args is None:
        cli_args = sys.argv[1:]

    # Parse arguments
    parser = create_enhanced_parser()
    args = parser.parse_args(cli_args)

    try:
        # Load tasks for the specified domain
        from tau2.registry import registry

        # Use task_set_name if specified, otherwise use domain
        task_set_name = args.task_set_name or args.domain
        get_tasks_func = registry.get_tasks_loader(task_set_name)
        tasks = get_tasks_func()

        # Filter tasks if task_ids specified
        if args.task_ids:
            tasks = [task for task in tasks if task.id in args.task_ids]
        elif args.num_tasks:
            tasks = tasks[:args.num_tasks]

        if not tasks:
            print("❌ No tasks found matching the criteria")
            sys.exit(1)

        print(f"Running enhanced simulation with {len(tasks)} tasks...")

        # Parse LLM arguments
        try:
            llm_args_agent = json.loads(args.agent_llm_args)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON for --agent-llm-args: {args.agent_llm_args}")
            sys.exit(1)

        try:
            llm_args_user = json.loads(args.user_llm_args)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON for --user-llm-args: {args.user_llm_args}")
            sys.exit(1)

        # Run enhanced simulation
        results, (main_path, logs_path) = run_enhanced_simulation(
            domain=args.domain,
            tasks=tasks,
            agent=args.agent,
            user=args.user,
            llm_agent=args.agent_llm,
            llm_args_agent=llm_args_agent,
            llm_user=args.user_llm,
            llm_args_user=llm_args_user,
            num_trials=args.num_trials,
            max_steps=args.max_steps,
            max_errors=args.max_errors,
            max_concurrency=args.max_concurrency,
            seed=args.seed,
            log_level=args.log_level,
            save_to=args.save_to
        )

        print(f"\n🎉 Enhanced simulation completed!")
        print(f"📊 Results saved to: {main_path}")
        if logs_path:
            print(f"🔍 Enhanced logs saved to: {logs_path}")

        # Print summary
        enhanced_count = sum(1 for sim in results.simulations if sim.enhanced_logging_enabled)
        total_exec_logs = sum(len(sim.execution_logs) if sim.execution_logs else 0 for sim in results.simulations)
        total_state_snaps = sum(len(sim.state_snapshots) if sim.state_snapshots else 0 for sim in results.simulations)

        print(f"📈 Enhanced logging summary:")
        print(f"   - Simulations with enhanced logs: {enhanced_count}/{len(results.simulations)}")
        print(f"   - Total execution logs captured: {total_exec_logs}")
        print(f"   - Total state snapshots captured: {total_state_snaps}")

    except Exception as e:
        print(f"❌ Enhanced simulation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)