"""
Action Check Analysis Module

Shared utilities for analyzing action check failures in tau2 simulations.
This module provides functions to compare expected vs actual tool calls
and generate detailed diff information.
"""

from typing import Dict, List, Any, Optional


def find_tool_calls_in_trajectory(trajectory: List[Dict]) -> List[Dict]:
    """
    Extract all tool calls from the trajectory/messages.

    Args:
        trajectory: List of message dictionaries from simulation

    Returns:
        List of tool call dictionaries with standardized format
    """
    tool_calls = []

    for msg in trajectory:
        if msg.get('role') in ['assistant', 'user']:
            if 'tool_calls' in msg and msg['tool_calls']:
                for tc in msg['tool_calls']:
                    tool_calls.append({
                        'id': tc.get('id'),
                        'name': tc.get('name'),
                        'arguments': tc.get('arguments', {}),
                        'requestor': msg['role']
                    })

    return tool_calls


def compare_arguments(expected: Dict, actual: Dict, compare_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Compare expected vs actual arguments.

    Args:
        expected: Expected argument dictionary
        actual: Actual argument dictionary
        compare_keys: Optional list of keys to compare (if None, compares all expected keys)

    Returns:
        Dict with 'matches', 'missing', 'extra', 'different' keys containing comparison results
    """
    if compare_keys is None:
        # Compare all keys from expected
        compare_keys = list(expected.keys())

    matches = {}
    missing = {}
    extra = {}
    different = {}

    for key in compare_keys:
        if key not in expected:
            continue

        expected_val = expected.get(key)
        actual_val = actual.get(key)

        if key not in actual:
            missing[key] = expected_val
        elif expected_val == actual_val:
            matches[key] = expected_val
        else:
            different[key] = {
                'expected': expected_val,
                'actual': actual_val
            }

    # Find extra keys not in compare_keys
    for key in actual:
        if key not in compare_keys and key not in expected:
            extra[key] = actual[key]

    return {
        'matches': matches,
        'missing': missing,
        'extra': extra,
        'different': different
    }


def analyze_action_check(action_check: Dict, trajectory: List[Dict]) -> Dict[str, Any]:
    """
    Analyze a single action check failure.

    Args:
        action_check: Action check dictionary from reward_info
        trajectory: List of messages from simulation

    Returns:
        Detailed analysis dictionary with expected action, actual behavior, and comparison
    """
    action = action_check['action']
    action_match = action_check['action_match']

    # Get expected action details
    expected = {
        'action_id': action['action_id'],
        'requestor': action.get('requestor', 'assistant'),
        'name': action['name'],
        'arguments': action['arguments'],
        'compare_args': action.get('compare_args'),
        'info': action.get('info')
    }

    # Find all tool calls in trajectory
    all_tool_calls = find_tool_calls_in_trajectory(trajectory)

    # Find matching tool calls (by name)
    matching_by_name = [
        tc for tc in all_tool_calls
        if tc['name'] == expected['name']
    ]

    # Find closest match (if any)
    closest_match = None
    best_score = 0

    for tc in matching_by_name:
        # Compare arguments
        compare_keys = expected['compare_args'] if expected['compare_args'] else list(expected['arguments'].keys())
        comparison = compare_arguments(expected['arguments'], tc['arguments'], compare_keys)

        # Calculate similarity score
        total_keys = len(compare_keys) if compare_keys else 0
        matching_keys = len(comparison['matches'])
        score = matching_keys / total_keys if total_keys > 0 else 0

        if score > best_score:
            best_score = score
            closest_match = {
                'tool_call': tc,
                'comparison': comparison,
                'similarity': score
            }

    return {
        'expected': expected,
        'action_match': action_match,
        'all_tool_calls_with_name': matching_by_name,
        'closest_match': closest_match,
        'all_tool_calls': all_tool_calls
    }


def get_failure_category(analysis: Dict[str, Any]) -> str:
    """
    Categorize the type of action check failure.

    Args:
        analysis: Analysis dictionary from analyze_action_check()

    Returns:
        String category: 'never_called', 'called_but_no_match', 'called_with_wrong_args'
    """
    if not analysis['all_tool_calls_with_name']:
        return 'never_called'
    elif not analysis['closest_match']:
        return 'called_but_no_match'
    else:
        return 'called_with_wrong_args'


def get_failure_summary(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a concise summary of the action check failure.

    Args:
        analysis: Analysis dictionary from analyze_action_check()

    Returns:
        Summary dictionary with key failure information
    """
    expected = analysis['expected']
    category = get_failure_category(analysis)

    summary = {
        'tool_name': expected['name'],
        'action_id': expected['action_id'],
        'category': category,
        'expected_args': expected['arguments'],
        'compare_args': expected['compare_args'],
    }

    if category == 'never_called':
        all_tools_called = set(tc['name'] for tc in analysis['all_tool_calls'])
        summary['tools_actually_called'] = list(all_tools_called)
        summary['call_count'] = 0
    elif category == 'called_but_no_match':
        summary['call_count'] = len(analysis['all_tool_calls_with_name'])
        summary['all_attempts'] = [tc['arguments'] for tc in analysis['all_tool_calls_with_name']]
    else:  # called_with_wrong_args
        closest = analysis['closest_match']
        summary['call_count'] = len(analysis['all_tool_calls_with_name'])
        summary['similarity'] = closest['similarity']
        summary['actual_args'] = closest['tool_call']['arguments']
        summary['diff'] = {
            'matching': closest['comparison']['matches'],
            'different': closest['comparison']['different'],
            'missing': closest['comparison']['missing'],
            'extra': closest['comparison']['extra']
        }

    return summary
