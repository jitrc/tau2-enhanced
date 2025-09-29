"""
Enhanced CLI interface that wraps tau2-bench CLI with enhanced logging capabilities.
"""

import sys
import argparse
import os
import json
import time
from pathlib import Path
from typing import Optional, List

from tau2.run import get_options
from tau2.config import *
from tau2_enhanced import run_enhanced_simulation

# Rich CLI formatting constants
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a colorful header."""
    print(f"{Colors.HEADER}{Colors.BOLD}🚀 {text}{Colors.ENDC}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_progress(current: int, total: int, desc: str = "Progress"):
    """Print a simple progress indicator."""
    percentage = (current / total) * 100 if total > 0 else 0
    bar_length = 30
    filled_length = int(bar_length * current // total) if total > 0 else 0
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f"\r🔄 {desc}: |{bar}| {percentage:.1f}% ({current}/{total})", end='', flush=True)
    if current == total:
        print()  # New line when complete


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
        help=f"Logging level (case insensitive). Valid levels: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL. Default is {DEFAULT_LOG_LEVEL}."
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

    # Print welcome banner
    print_header("tau2-enhanced: Advanced AI Agent Evaluation")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    # Parse arguments
    parser = create_enhanced_parser()
    args = parser.parse_args(cli_args)

    # Convert log level to uppercase for loguru compatibility
    args.log_level = args.log_level.upper()

    # Validate log level
    valid_log_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
    if args.log_level not in valid_log_levels:
        print_error(f"Invalid log level: {args.log_level}")
        print_info(f"Valid log levels: {', '.join(valid_log_levels)}")
        sys.exit(1)

    try:
        print_info(f"Initializing enhanced simulation for domain: {Colors.BOLD}{args.domain}{Colors.ENDC}")

        # Load tasks for the specified domain
        from tau2.registry import registry

        # Use task_set_name if specified, otherwise use domain
        task_set_name = args.task_set_name or args.domain
        get_tasks_func = registry.get_tasks_loader(task_set_name)

        print_info("Loading tasks from registry...")
        tasks = get_tasks_func()

        # Filter tasks if task_ids specified
        if args.task_ids:
            tasks = [task for task in tasks if task.id in args.task_ids]
            print_info(f"Filtered to specific task IDs: {', '.join(args.task_ids)}")
        elif args.num_tasks:
            tasks = tasks[:args.num_tasks]
            print_info(f"Limited to first {args.num_tasks} tasks")

        if not tasks:
            print_error("No tasks found matching the criteria")
            sys.exit(1)

        print_success(f"Loaded {len(tasks)} task(s) for evaluation")

        # Display configuration summary
        print(f"\n{Colors.UNDERLINE}Configuration Summary:{Colors.ENDC}")
        print(f"🎯 Domain: {Colors.BOLD}{args.domain}{Colors.ENDC}")
        print(f"🤖 Agent: {Colors.BOLD}{args.agent}{Colors.ENDC} ({args.agent_llm})")
        print(f"👤 User: {Colors.BOLD}{args.user}{Colors.ENDC} ({args.user_llm})")
        print(f"🔢 Trials per task: {Colors.BOLD}{args.num_trials}{Colors.ENDC}")
        print(f"⚡ Max concurrency: {Colors.BOLD}{args.max_concurrency}{Colors.ENDC}")
        print(f"🎲 Random seed: {Colors.BOLD}{args.seed}{Colors.ENDC}")

        # Parse LLM arguments with error handling
        print_info("Parsing LLM configuration...")
        try:
            llm_args_agent = json.loads(args.agent_llm_args)
        except json.JSONDecodeError:
            print_error(f"Invalid JSON for --agent-llm-args: {args.agent_llm_args}")
            print_info("Expected format: '{\"temperature\": 0.0, \"max_tokens\": 1000}'")
            sys.exit(1)

        try:
            llm_args_user = json.loads(args.user_llm_args)
        except json.JSONDecodeError:
            print_error(f"Invalid JSON for --user-llm-args: {args.user_llm_args}")
            print_info("Expected format: '{\"temperature\": 0.0, \"max_tokens\": 1000}'")
            sys.exit(1)

        print_success("Configuration validated successfully")

        # Start simulation with progress indication
        print(f"\n{Colors.HEADER}{Colors.BOLD}🚀 Starting Enhanced Simulation{Colors.ENDC}")
        print(f"{'─'*60}")

        start_time = time.time()

        # Simulate progress during execution
        total_operations = len(tasks) * args.num_trials
        print_info(f"Executing {total_operations} simulation(s) with enhanced logging...")

        # Run enhanced simulation
        results, enhanced_logs, (main_path, logs_path) = run_enhanced_simulation(
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

        execution_time = time.time() - start_time

        # Success banner
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 SIMULATION COMPLETED SUCCESSFULLY! 🎉{Colors.ENDC}")
        print(f"{'='*60}")

        # Results summary with rich formatting
        print_success(f"Execution completed in {execution_time:.2f} seconds")
        print_info(f"📊 Standard results: {Colors.BOLD}{main_path}{Colors.ENDC}")
        if logs_path:
            print_info(f"🔍 Enhanced logs: {Colors.BOLD}{logs_path}{Colors.ENDC}")

        # Enhanced logging statistics from the enhanced_logs dict
        summary = enhanced_logs.get('summary', {})
        total_exec_logs = summary.get('total_execution_logs', 0)
        total_state_snaps = summary.get('total_state_snapshots', 0)
        environments_with_logs = summary.get('environments_with_logs', 0)
        enhanced_count = 1 if total_exec_logs > 0 or total_state_snaps > 0 else 0

        # Calculate some basic statistics
        total_sims = len(results.simulations)
        # Compute success based on reward_info (tau2-bench doesn't have a direct 'success' field)
        successful_sims = sum(1 for sim in results.simulations
                             if sim.reward_info and sim.reward_info.reward and sim.reward_info.reward > 0)
        success_rate = (successful_sims / total_sims * 100) if total_sims > 0 else 0

        print(f"\n{Colors.UNDERLINE}📈 Enhanced Logging Summary:{Colors.ENDC}")
        print(f"   🔧 Enhanced simulations: {Colors.BOLD}{enhanced_count}/{total_sims}{Colors.ENDC}")
        print(f"   📝 Execution events captured: {Colors.BOLD}{total_exec_logs:,}{Colors.ENDC}")
        print(f"   📸 State snapshots taken: {Colors.BOLD}{total_state_snaps:,}{Colors.ENDC}")
        print(f"   ✅ Success rate: {Colors.BOLD}{success_rate:.1f}%{Colors.ENDC}")

        # Provide next steps
        print(f"\n{Colors.UNDERLINE}🔍 Next Steps:{Colors.ENDC}")
        analyze_path = logs_path if logs_path else main_path
        print(f"   💡 Analyze logs: {Colors.OKCYAN}python scripts/analyze_simple_logs.py {analyze_path}{Colors.ENDC}")
        print(f"   📊 View dashboard: {Colors.OKCYAN}tau2 view{Colors.ENDC}")
        print(f"   🔬 Deep dive: Load logs in Jupyter notebook for detailed analysis")

    except KeyboardInterrupt:
        print_warning("\nSimulation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Enhanced simulation failed: {str(e)}")

        # Provide helpful debugging information
        print(f"\n{Colors.UNDERLINE}🔧 Debugging Information:{Colors.ENDC}")
        print_info("Check the following:")
        print("   • Domain name is correct and available")
        print("   • LLM credentials are properly configured")
        print("   • tau2-bench dependencies are installed")
        print("   • Sufficient disk space for logs")

        # Show full traceback in debug mode
        if args.log_level.lower() in ['debug', 'trace']:
            print(f"\n{Colors.UNDERLINE}📋 Full Traceback:{Colors.ENDC}")
            import traceback
            traceback.print_exc()
        else:
            print_info("Run with --log-level debug for full traceback")

        sys.exit(1)