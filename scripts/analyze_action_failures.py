#!/usr/bin/env python3
"""
Analyze Action Check Failures

This script analyzes simulation results and provides detailed information about
action check failures, showing what was expected vs what actually happened.

Usage:
    python analyze_action_failures.py <results_file.json>
    python analyze_action_failures.py <results_file.json> --task-id task_123
    python analyze_action_failures.py <results_file.json> --failed-only
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import argparse

# Import shared action check analysis functions
from tau2_enhanced.analysis.action_check_analysis import (
    find_tool_calls_in_trajectory,
    compare_arguments,
    analyze_action_check
)


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def load_results(file_path: str) -> Dict[str, Any]:
    """Load simulation results from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def print_action_failure(analysis: Dict, task_id: str, trial_idx: int):
    """Print detailed analysis of an action failure."""
    expected = analysis['expected']
    closest = analysis['closest_match']

    print(f"\n{'='*100}")
    print(f"{Colors.RED}{Colors.BOLD}❌ ACTION CHECK FAILURE{Colors.END}")
    print(f"{Colors.CYAN}Task ID:{Colors.END} {task_id}")
    print(f"{Colors.CYAN}Trial:{Colors.END} {trial_idx}")
    print(f"{'='*100}")

    # Print expected action
    print(f"\n{Colors.YELLOW}{Colors.BOLD}EXPECTED ACTION:{Colors.END}")
    print(f"  {Colors.CYAN}Action ID:{Colors.END} {expected['action_id']}")
    print(f"  {Colors.CYAN}Tool Name:{Colors.END} {expected['name']}")
    print(f"  {Colors.CYAN}Requestor:{Colors.END} {expected['requestor']}")

    if expected['info']:
        print(f"  {Colors.CYAN}Info:{Colors.END} {expected['info']}")

    print(f"\n  {Colors.CYAN}Expected Arguments:{Colors.END}")
    for key, val in expected['arguments'].items():
        marker = "  *" if expected['compare_args'] and key in expected['compare_args'] else "   "
        print(f"    {marker} {Colors.BOLD}{key}:{Colors.END} {json.dumps(val)}")

    if expected['compare_args']:
        print(f"\n  {Colors.YELLOW}Note: Arguments marked with * are used for comparison{Colors.END}")

    # Print what actually happened
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}ACTUAL BEHAVIOR:{Colors.END}")

    if not analysis['all_tool_calls_with_name']:
        print(f"  {Colors.RED}❌ Tool '{expected['name']}' was NEVER called{Colors.END}")

        # Show all tools that were called
        all_tools = set(tc['name'] for tc in analysis['all_tool_calls'])
        if all_tools:
            print(f"\n  {Colors.CYAN}Tools that were called:{Colors.END}")
            for tool in sorted(all_tools):
                count = sum(1 for tc in analysis['all_tool_calls'] if tc['name'] == tool)
                print(f"    - {tool} ({count} time{'s' if count > 1 else ''})")
        else:
            print(f"\n  {Colors.RED}No tools were called at all!{Colors.END}")

    elif not closest:
        print(f"  {Colors.RED}❌ Tool '{expected['name']}' was called {len(analysis['all_tool_calls_with_name'])} time(s), but none matched{Colors.END}")

        # Show all attempts with detailed comparison
        for i, tc in enumerate(analysis['all_tool_calls_with_name'], 1):
            print(f"\n  {Colors.YELLOW}Attempt {i}:{Colors.END}")

            # Compare this attempt's arguments against expected
            compare_keys = expected['compare_args'] if expected['compare_args'] else list(expected['arguments'].keys())
            comp = compare_arguments(expected['arguments'], tc['arguments'], compare_keys)

            # Calculate similarity
            total_keys = len(compare_keys) if compare_keys else 0
            matching_keys = len(comp['matches'])
            similarity = matching_keys / total_keys if total_keys > 0 else 0
            print(f"    {Colors.CYAN}Similarity:{Colors.END} {similarity:.0%}")

            # Show comparison
            if comp['matches']:
                print(f"\n    {Colors.GREEN}{Colors.BOLD}✓ Matching:{Colors.END}")
                for key, val in comp['matches'].items():
                    print(f"      ✓ {Colors.BOLD}{key}:{Colors.END} {json.dumps(val)}")

            if comp['different']:
                print(f"\n    {Colors.RED}{Colors.BOLD}✗ Different:{Colors.END}")
                for key, vals in comp['different'].items():
                    print(f"      ✗ {Colors.BOLD}{key}:{Colors.END}")
                    print(f"        {Colors.CYAN}Expected:{Colors.END} {json.dumps(vals['expected'])}")
                    print(f"        {Colors.RED}Actual:{Colors.END}   {json.dumps(vals['actual'])}")

            if comp['missing']:
                print(f"\n    {Colors.RED}{Colors.BOLD}✗ Missing:{Colors.END}")
                for key, val in comp['missing'].items():
                    print(f"      ✗ {Colors.BOLD}{key}:{Colors.END} {json.dumps(val)} (not provided)")

            if comp['extra']:
                print(f"\n    {Colors.YELLOW}{Colors.BOLD}⚠ Extra:{Colors.END}")
                for key, val in comp['extra'].items():
                    print(f"      ⚠ {Colors.BOLD}{key}:{Colors.END} {json.dumps(val)} (not expected)")

    else:
        # Show closest match
        tc = closest['tool_call']
        comp = closest['comparison']
        similarity = closest['similarity']

        print(f"  {Colors.YELLOW}✓ Tool '{expected['name']}' was called, but with incorrect arguments{Colors.END}")
        print(f"  {Colors.CYAN}Similarity:{Colors.END} {similarity:.0%}")

        if len(analysis['all_tool_calls_with_name']) > 1:
            print(f"  {Colors.CYAN}Note:{Colors.END} Tool was called {len(analysis['all_tool_calls_with_name'])} times, showing closest match")

        print(f"\n  {Colors.GREEN}{Colors.BOLD}✓ MATCHING ARGUMENTS:{Colors.END}")
        if comp['matches']:
            for key, val in comp['matches'].items():
                print(f"    ✓ {Colors.BOLD}{key}:{Colors.END} {json.dumps(val)}")
        else:
            print(f"    {Colors.YELLOW}(none){Colors.END}")

        if comp['different']:
            print(f"\n  {Colors.RED}{Colors.BOLD}✗ DIFFERENT VALUES:{Colors.END}")
            for key, vals in comp['different'].items():
                print(f"    ✗ {Colors.BOLD}{key}:{Colors.END}")
                print(f"      {Colors.CYAN}Expected:{Colors.END} {json.dumps(vals['expected'])}")
                print(f"      {Colors.RED}Actual:{Colors.END}   {json.dumps(vals['actual'])}")

        if comp['missing']:
            print(f"\n  {Colors.RED}{Colors.BOLD}✗ MISSING ARGUMENTS:{Colors.END}")
            for key, val in comp['missing'].items():
                print(f"    ✗ {Colors.BOLD}{key}:{Colors.END} {json.dumps(val)} (was not provided)")

        if comp['extra']:
            print(f"\n  {Colors.YELLOW}{Colors.BOLD}⚠ EXTRA ARGUMENTS:{Colors.END}")
            for key, val in comp['extra'].items():
                print(f"    ⚠ {Colors.BOLD}{key}:{Colors.END} {json.dumps(val)} (not in expected)")

        # Show full actual arguments for reference
        print(f"\n  {Colors.CYAN}Full Actual Arguments:{Colors.END}")
        print(json.dumps(tc['arguments'], indent=4))


def print_action_success(expected: Dict, task_id: str, trial_idx: int, show_details: bool = False):
    """Print brief info about successful action check."""
    if show_details:
        print(f"\n{Colors.GREEN}✓ Action Check Passed:{Colors.END} {expected['action_id']} - {expected['name']}")


def analyze_simulation_results(results_file: str, task_filter: Optional[str] = None,
                               failed_only: bool = True, show_success: bool = False):
    """Analyze simulation results and print detailed failure information."""

    print(f"\n{Colors.BOLD}{'='*100}")
    print(f"ACTION CHECK FAILURE ANALYSIS")
    print(f"{'='*100}{Colors.END}")
    print(f"\n{Colors.CYAN}Results File:{Colors.END} {results_file}")

    results = load_results(results_file)

    # Stats
    total_trials = 0
    total_action_checks = 0
    total_failures = 0
    failures_by_action = defaultdict(int)
    tasks_with_failures = set()

    # Support both 'trials' and 'simulations' format
    trials = results.get('trials', results.get('simulations', []))

    if task_filter:
        trials = [t for t in trials if t.get('task_id') == task_filter]
        print(f"{Colors.CYAN}Filter:{Colors.END} Task ID = {task_filter}")

    print(f"\n{Colors.CYAN}Total Trials:{Colors.END} {len(trials)}")

    if not trials:
        print(f"\n{Colors.YELLOW}No trials found!{Colors.END}")
        return

    print(f"\n{Colors.BOLD}Analyzing action checks...{Colors.END}\n")

    for trial in trials:
        task_id = trial.get('task_id', 'unknown')
        trial_idx = trial.get('trial_idx', 0)
        total_trials += 1

        # Get reward info
        reward_info = trial.get('reward_info', {})
        action_checks = reward_info.get('action_checks', [])
        trajectory = trial.get('trajectory', trial.get('messages', []))

        if not action_checks:
            continue

        total_action_checks += len(action_checks)

        for action_check in action_checks:
            action = action_check['action']
            action_match = action_check['action_match']

            if not action_match:
                # Failure!
                total_failures += 1
                failures_by_action[action['name']] += 1
                tasks_with_failures.add(task_id)

                # Analyze and print
                analysis = analyze_action_check(action_check, trajectory)
                print_action_failure(analysis, task_id, trial_idx)

            elif show_success:
                # Success
                print_action_success(action, task_id, trial_idx, show_details=True)

    # Print summary
    print(f"\n{'='*100}")
    print(f"{Colors.BOLD}SUMMARY{Colors.END}")
    print(f"{'='*100}")
    print(f"{Colors.CYAN}Total Trials:{Colors.END} {total_trials}")
    print(f"{Colors.CYAN}Total Action Checks:{Colors.END} {total_action_checks}")
    print(f"{Colors.RED}Total Failures:{Colors.END} {total_failures}")
    print(f"{Colors.GREEN}Success Rate:{Colors.END} {(1 - total_failures/total_action_checks)*100:.1f}%" if total_action_checks > 0 else "N/A")
    print(f"{Colors.CYAN}Tasks with Failures:{Colors.END} {len(tasks_with_failures)}")

    if failures_by_action:
        print(f"\n{Colors.BOLD}Failures by Action:{Colors.END}")
        for action_name, count in sorted(failures_by_action.items(), key=lambda x: x[1], reverse=True):
            print(f"  {action_name}: {Colors.RED}{count}{Colors.END} failure(s)")

    print(f"\n{'='*100}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze action check failures in simulation results",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'results_file',
        help='Path to simulation results JSON file'
    )

    parser.add_argument(
        '--task-id',
        help='Filter by specific task ID',
        default=None
    )

    parser.add_argument(
        '--show-success',
        action='store_true',
        help='Also show successful action checks'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Show all trials (including those without failures)'
    )

    args = parser.parse_args()

    if not Path(args.results_file).exists():
        print(f"{Colors.RED}Error: File not found: {args.results_file}{Colors.END}")
        sys.exit(1)

    try:
        analyze_simulation_results(
            args.results_file,
            task_filter=args.task_id,
            failed_only=not args.all,
            show_success=args.show_success
        )
    except Exception as e:
        print(f"\n{Colors.RED}Error analyzing results:{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
