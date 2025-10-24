#!/usr/bin/env python3
"""
Generate Action Failure Analysis HTML Report

This script generates an interactive HTML report from simulation results,
showing detailed action check failures with expected vs actual argument diffs.

Usage:
    python generate_action_failure_report.py <results_file.json>
    python generate_action_failure_report.py <results_file.json> -o custom_output_dir/
    python generate_action_failure_report.py <results_file.json> --output-file custom_name.html

Output: analysis_results/<results_filename>/action_failure_report.html
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import argparse
from datetime import datetime

# Import shared action check analysis functions
from tau2_enhanced.analysis.action_check_analysis import (
    find_tool_calls_in_trajectory,
    compare_arguments,
    analyze_action_check
)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tau2 Simulation Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }

        .header-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
            padding: 20px;
            background: #ecf0f1;
            border-radius: 6px;
        }

        .info-item {
            display: flex;
            flex-direction: column;
        }

        .info-label {
            font-size: 0.85em;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }

        .info-value {
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
        }

        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border: 2px solid;
        }

        .stat-card.success {
            background: #d5f4e6;
            border-color: #27ae60;
        }

        .stat-card.warning {
            background: #ffeaa7;
            border-color: #fdcb6e;
        }

        .stat-card.error {
            background: #fab1a0;
            border-color: #e17055;
        }

        .stat-card.info {
            background: #dfe6e9;
            border-color: #74b9ff;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9em;
            color: #2c3e50;
        }

        .task-section {
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 6px;
            overflow: hidden;
        }

        .task-header {
            background: #3498db;
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }

        .task-header:hover {
            background: #2980b9;
        }

        .task-header.failed {
            background: #e74c3c;
        }

        .task-header.failed:hover {
            background: #c0392b;
        }

        .task-title {
            font-size: 1.1em;
            font-weight: 600;
        }

        .task-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            background: rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .expand-icon {
            transition: transform 0.3s;
            font-size: 1.2em;
        }

        .task-section.expanded .expand-icon {
            transform: rotate(180deg);
        }

        .task-content {
            display: none;
            padding: 20px;
            background: #fafafa;
        }

        .task-section.expanded .task-content {
            display: block;
        }

        .section-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
            margin: 20px 0 15px 0;
            padding: 10px 0;
            border-bottom: 2px solid #3498db;
        }

        .section-title:first-child {
            margin-top: 0;
        }

        .detail-grid {
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 10px 20px;
            margin-bottom: 20px;
        }

        .detail-label {
            font-weight: 600;
            color: #7f8c8d;
        }

        .detail-value {
            color: #2c3e50;
        }

        .action-failure {
            background: white;
            border: 2px solid #e74c3c;
            border-radius: 6px;
            padding: 20px;
            margin: 15px 0;
        }

        .action-success {
            background: white;
            border: 2px solid #27ae60;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
        }

        .failure-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }

        .failure-icon {
            font-size: 1.5em;
            color: #e74c3c;
        }

        .success-icon {
            font-size: 1.2em;
            color: #27ae60;
        }

        .failure-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #2c3e50;
        }

        .expected-action, .actual-behavior {
            margin: 15px 0;
            padding: 15px;
            border-radius: 6px;
        }

        .expected-action {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }

        .actual-behavior {
            background: #f8d7da;
            border-left: 4px solid #e74c3c;
        }

        .subsection-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.05em;
        }

        .arguments-list {
            margin: 10px 0;
            padding-left: 20px;
        }

        .arg-item {
            margin: 5px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
        }

        .arg-item.compared {
            font-weight: 600;
        }

        .arg-key {
            color: #8e44ad;
        }

        .arg-value {
            color: #16a085;
        }

        .comparison-section {
            margin: 15px 0;
        }

        .match-item {
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 4px;
            background: #d5f4e6;
            border-left: 3px solid #27ae60;
        }

        .diff-item {
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 4px;
            background: #fab1a0;
            border-left: 3px solid #e74c3c;
        }

        .missing-item {
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 4px;
            background: #ffeaa7;
            border-left: 3px solid #fdcb6e;
        }

        .extra-item {
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 4px;
            background: #dfe6e9;
            border-left: 3px solid #74b9ff;
        }

        .value-comparison {
            margin-left: 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .expected-val {
            color: #27ae60;
        }

        .actual-val {
            color: #e74c3c;
        }

        .similarity-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }

        .similarity-high {
            background: #d5f4e6;
            color: #27ae60;
        }

        .similarity-medium {
            background: #ffeaa7;
            color: #d68910;
        }

        .similarity-low {
            background: #fab1a0;
            color: #e74c3c;
        }

        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            margin: 10px 0;
        }

        .no-failures {
            padding: 20px;
            text-align: center;
            color: #27ae60;
            font-size: 1.1em;
            background: #d5f4e6;
            border-radius: 6px;
            margin: 20px 0;
        }

        .trajectory-info {
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
        }

        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
        }

        .control-btn {
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
        }

        .control-btn:hover {
            background: #2980b9;
        }

        .task-counter {
            padding: 10px 0;
            font-size: 1em;
            font-weight: 600;
            color: #2c3e50;
        }

        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>

    <script>
        // Toggle task expansion
        document.querySelectorAll('.task-header').forEach(header => {
            header.addEventListener('click', function() {
                this.parentElement.classList.toggle('expanded');
            });
        });

        // Collapse/Expand all button
        function toggleAllTasks() {
            const allTasks = document.querySelectorAll('.task-section');
            const anyExpanded = Array.from(allTasks).some(task => task.classList.contains('expanded'));

            allTasks.forEach(task => {
                if (anyExpanded) {
                    task.classList.remove('expanded');
                } else {
                    task.classList.add('expanded');
                }
            });

            const btn = document.getElementById('toggle-all-btn');
            btn.textContent = anyExpanded ? 'Expand All' : 'Collapse All';
        }

        // Update task counter
        function updateTaskCounter() {
            const allTasks = document.querySelectorAll('.task-section');
            const visibleTasks = Array.from(allTasks).filter(task => {
                return task.style.display !== 'none';
            });

            const counter = document.getElementById('task-counter');
            counter.textContent = `Showing: ${visibleTasks.length} / ${allTasks.length} tasks`;
        }

        // Show all tasks
        function showAll() {
            const allTasks = document.querySelectorAll('.task-section');
            allTasks.forEach(task => {
                task.style.display = 'block';
            });
            updateTaskCounter();
        }

        // Show only tasks with failures
        function showFailedOnly() {
            const allTasks = document.querySelectorAll('.task-section');
            allTasks.forEach(task => {
                const hasFailures = task.getAttribute('data-has-failures') === 'true';
                task.style.display = hasFailures ? 'block' : 'none';
            });
            updateTaskCounter();
        }

        // Show only tasks where tool was called but with wrong args (not "never called")
        function showCalledWithDiff() {
            const allTasks = document.querySelectorAll('.task-section');
            allTasks.forEach(task => {
                const hasCalledFailures = task.getAttribute('data-has-called-failures') === 'true';
                task.style.display = hasCalledFailures ? 'block' : 'none';
            });
            updateTaskCounter();
        }

        // Initialize counter on page load
        document.addEventListener('DOMContentLoaded', function() {
            updateTaskCounter();
        });
    </script>
</body>
</html>
"""


def format_json(obj: Any) -> str:
    """Format JSON with proper indentation."""
    return json.dumps(obj, indent=2)


def get_similarity_class(similarity: float) -> str:
    """Get CSS class based on similarity score."""
    if similarity >= 0.8:
        return "similarity-high"
    elif similarity >= 0.5:
        return "similarity-medium"
    else:
        return "similarity-low"


def render_action_failure(analysis: Dict, task_id: str, trial_idx: int) -> str:
    """Render an action failure with detailed diff."""
    expected = analysis['expected']
    closest = analysis['closest_match']

    html = '<div class="action-failure">'

    # Header
    html += '<div class="failure-header">'
    html += '<span class="failure-icon">❌</span>'
    html += f'<div class="failure-title">Action Check Failure: {expected["name"]}</div>'
    html += '</div>'

    # Expected Action
    html += '<div class="expected-action">'
    html += '<div class="subsection-title">📋 EXPECTED ACTION</div>'
    html += f'<div class="detail-grid">'
    html += f'<div class="detail-label">Action ID:</div><div class="detail-value">{expected["action_id"]}</div>'
    html += f'<div class="detail-label">Tool Name:</div><div class="detail-value"><code>{expected["name"]}</code></div>'
    html += f'<div class="detail-label">Requestor:</div><div class="detail-value">{expected["requestor"]}</div>'
    html += '</div>'

    if expected.get('info'):
        html += f'<div style="margin-top: 10px;"><strong>Info:</strong> {expected["info"]}</div>'

    html += '<div class="subsection-title" style="margin-top: 15px;">Expected Arguments:</div>'
    html += '<div class="arguments-list">'
    for key, val in expected['arguments'].items():
        compared = expected.get('compare_args') and key in expected['compare_args']
        marker = '⭐' if compared else '•'
        css_class = 'arg-item compared' if compared else 'arg-item'
        html += f'<div class="{css_class}">{marker} <span class="arg-key">{key}</span>: <span class="arg-value">{format_json(val)}</span></div>'
    html += '</div>'

    if expected.get('compare_args'):
        html += '<div style="margin-top: 10px; font-size: 0.9em; color: #7f8c8d;">⭐ Arguments marked with star are used for comparison</div>'

    html += '</div>'  # End expected-action

    # Actual Behavior
    html += '<div class="actual-behavior">'
    html += '<div class="subsection-title">🔍 ACTUAL BEHAVIOR</div>'

    if not analysis['all_tool_calls_with_name']:
        html += f'<div style="color: #e74c3c; font-weight: 600;">❌ Tool \'{expected["name"]}\' was NEVER called</div>'

        # Show what was called
        all_tools = {}
        for tc in analysis['all_tool_calls']:
            name = tc['name']
            all_tools[name] = all_tools.get(name, 0) + 1

        if all_tools:
            html += '<div style="margin-top: 15px;"><strong>Tools that were called:</strong></div>'
            html += '<ul style="margin-left: 20px;">'
            for tool, count in sorted(all_tools.items()):
                html += f'<li><code>{tool}</code> ({count} time{"s" if count > 1 else ""})</li>'
            html += '</ul>'
        else:
            html += '<div style="margin-top: 10px; color: #e74c3c;">No tools were called at all!</div>'

    elif not closest:
        html += f'<div style="color: #e74c3c; font-weight: 600;">❌ Tool \'{expected["name"]}\' was called {len(analysis["all_tool_calls_with_name"])} time(s), but none matched</div>'

        # Show all attempts with detailed comparison
        html += '<div style="margin-top: 20px;">'
        for i, tc in enumerate(analysis['all_tool_calls_with_name'], 1):
            html += f'<div style="border: 2px solid #ff9800; border-radius: 6px; padding: 15px; margin: 15px 0; background: #fff8e1;">'
            html += f'<div style="font-weight: 600; font-size: 1.05em; margin-bottom: 10px; color: #e65100;">Attempt {i}</div>'

            # Compare this attempt's arguments against expected
            compare_keys = expected['compare_args'] if expected['compare_args'] else list(expected['arguments'].keys())
            comp = compare_arguments(expected['arguments'], tc['arguments'], compare_keys)

            # Calculate similarity
            total_keys = len(compare_keys) if compare_keys else 0
            matching_keys = len(comp['matches'])
            similarity = matching_keys / total_keys if total_keys > 0 else 0
            html += f'<div style="margin-bottom: 10px;">Similarity: <span class="similarity-badge {get_similarity_class(similarity)}">{similarity:.0%}</span></div>'

            # Show comparison
            if comp['matches']:
                html += '<div style="margin-top: 10px;"><strong style="color: #27ae60;">✓ Matching:</strong></div>'
                for key, val in comp['matches'].items():
                    html += f'<div style="color: #27ae60; margin-left: 15px;">✓ <strong>{key}:</strong> <code>{format_json(val)}</code></div>'

            if comp['different']:
                html += '<div style="margin-top: 10px;"><strong style="color: #e74c3c;">✗ Different:</strong></div>'
                for key, vals in comp['different'].items():
                    html += f'<div style="margin-left: 15px; margin-top: 5px;">'
                    html += f'<div style="color: #e74c3c;">✗ <strong>{key}:</strong></div>'
                    html += f'<div style="margin-left: 20px;"><span style="color: #3498db;">Expected:</span> <code>{format_json(vals["expected"])}</code></div>'
                    html += f'<div style="margin-left: 20px;"><span style="color: #e74c3c;">Actual:</span> <code>{format_json(vals["actual"])}</code></div>'
                    html += '</div>'

            if comp['missing']:
                html += '<div style="margin-top: 10px;"><strong style="color: #e74c3c;">✗ Missing:</strong></div>'
                for key, val in comp['missing'].items():
                    html += f'<div style="color: #e74c3c; margin-left: 15px;">✗ <strong>{key}:</strong> <code>{format_json(val)}</code> (not provided)</div>'

            if comp['extra']:
                html += '<div style="margin-top: 10px;"><strong style="color: #f39c12;">⚠ Extra:</strong></div>'
                for key, val in comp['extra'].items():
                    html += f'<div style="color: #f39c12; margin-left: 15px;">⚠ <strong>{key}:</strong> <code>{format_json(val)}</code> (not expected)</div>'

            html += '</div>'
        html += '</div>'

    else:
        tc = closest['tool_call']
        comp = closest['comparison']
        similarity = closest['similarity']

        html += f'<div style="margin-bottom: 15px;">✓ Tool \'{expected["name"]}\' was called, but with incorrect arguments</div>'
        html += f'<div style="margin-bottom: 15px;">Similarity: <span class="similarity-badge {get_similarity_class(similarity)}">{similarity:.0%}</span></div>'

        if len(analysis['all_tool_calls_with_name']) > 1:
            html += f'<div style="font-size: 0.9em; color: #7f8c8d; margin-bottom: 15px;">Note: Tool was called {len(analysis["all_tool_calls_with_name"])} times, showing closest match</div>'

        # Matching Arguments
        html += '<div class="comparison-section">'
        html += '<div class="subsection-title">✓ MATCHING ARGUMENTS</div>'
        if comp['matches']:
            for key, val in comp['matches'].items():
                html += f'<div class="match-item">✓ <strong>{key}:</strong> <code>{format_json(val)}</code></div>'
        else:
            html += '<div style="color: #7f8c8d; font-style: italic;">(none)</div>'
        html += '</div>'

        # Different Values
        if comp['different']:
            html += '<div class="comparison-section">'
            html += '<div class="subsection-title">✗ DIFFERENT VALUES</div>'
            for key, vals in comp['different'].items():
                html += f'<div class="diff-item">'
                html += f'<strong>{key}:</strong>'
                html += '<div class="value-comparison">'
                html += f'<div class="expected-val">Expected: {format_json(vals["expected"])}</div>'
                html += f'<div class="actual-val">Actual: {format_json(vals["actual"])}</div>'
                html += '</div>'
                html += '</div>'
            html += '</div>'

        # Missing Arguments
        if comp['missing']:
            html += '<div class="comparison-section">'
            html += '<div class="subsection-title">✗ MISSING ARGUMENTS</div>'
            for key, val in comp['missing'].items():
                html += f'<div class="missing-item">✗ <strong>{key}:</strong> <code>{format_json(val)}</code> (was not provided)</div>'
            html += '</div>'

        # Extra Arguments
        if comp['extra']:
            html += '<div class="comparison-section">'
            html += '<div class="subsection-title">⚠ EXTRA ARGUMENTS</div>'
            for key, val in comp['extra'].items():
                html += f'<div class="extra-item">⚠ <strong>{key}:</strong> <code>{format_json(val)}</code> (not in expected)</div>'
            html += '</div>'

        # Full actual arguments
        html += '<div style="margin-top: 15px;">'
        html += '<div class="subsection-title">Full Actual Arguments:</div>'
        html += f'<div class="code-block">{format_json(tc["arguments"])}</div>'
        html += '</div>'

    html += '</div>'  # End actual-behavior
    html += '</div>'  # End action-failure

    return html


def render_action_success(expected: Dict) -> str:
    """Render a successful action check."""
    html = '<div class="action-success">'
    html += '<span class="success-icon">✓</span> '
    html += f'<strong>Action Check Passed:</strong> {expected["action_id"]} - <code>{expected["name"]}</code>'
    html += '</div>'
    return html


def render_task_details(trial: Dict) -> str:
    """Render Task Details section."""
    task_id = trial.get('task_id', 'unknown')
    goal = trial.get('goal', 'N/A')

    html = '<div class="section-title">📋 Task Details</div>'
    html += '<div class="detail-grid">'
    html += f'<div class="detail-label">Task ID:</div><div class="detail-value"><code>{task_id}</code></div>'
    html += f'<div class="detail-label">Goal:</div><div class="detail-value">{goal}</div>'
    html += '</div>'

    return html


def render_simulation_details(trial: Dict) -> str:
    """Render Simulation Details section."""
    reward_info = trial.get('reward_info', {})

    html = '<div class="section-title">🔬 Simulation Details</div>'
    html += '<div class="detail-grid">'
    html += f'<div class="detail-label">Trial Index:</div><div class="detail-value">{trial.get("trial_idx", 0)}</div>'
    html += f'<div class="detail-label">Total Reward:</div><div class="detail-value">{reward_info.get("total_reward", 0):.2f}</div>'
    html += f'<div class="detail-label">Goal Reward:</div><div class="detail-value">{reward_info.get("goal_reward", 0):.2f}</div>'

    # Count action checks (handle None)
    action_checks = reward_info.get('action_checks') or []
    html += f'<div class="detail-label">Action Checks:</div><div class="detail-value">{len(action_checks)}</div>'

    # Count passed/failed action checks
    passed = sum(1 for ac in action_checks if ac.get('action_match', False))
    failed = len(action_checks) - passed

    html += f'<div class="detail-label">Actions Passed:</div><div class="detail-value" style="color: #27ae60;">{passed}</div>'
    html += f'<div class="detail-label">Actions Failed:</div><div class="detail-value" style="color: #e74c3c;">{failed}</div>'
    html += '</div>'

    return html


def render_action_checks(trial: Dict) -> str:
    """Render action checks section with failures and successes."""
    reward_info = trial.get('reward_info', {})
    action_checks = reward_info.get('action_checks') or []
    trajectory = trial.get('trajectory', trial.get('messages', []))

    if not action_checks:
        return '<div class="no-failures">No action checks for this task</div>'

    html = '<div class="section-title">🎯 Action Checks</div>'

    failures = []
    successes = []

    for action_check in action_checks:
        if not action_check.get('action_match', False):
            analysis = analyze_action_check(action_check, trajectory)
            failures.append(render_action_failure(
                analysis,
                trial.get('task_id', 'unknown'),
                trial.get('trial_idx', 0)
            ))
        else:
            successes.append(render_action_success(action_check['action']))

    # Show failures first
    if failures:
        for failure_html in failures:
            html += failure_html

    # Then successes
    if successes:
        html += '<div style="margin-top: 20px;"><strong>Successful Action Checks:</strong></div>'
        for success_html in successes:
            html += success_html

    if not failures:
        html += '<div class="no-failures">✅ All action checks passed!</div>'

    return html


def render_task_section(trial: Dict, index: int) -> str:
    """Render a complete collapsible task section."""
    task_id = trial.get('task_id', 'unknown')
    reward_info = trial.get('reward_info', {})
    action_checks = reward_info.get('action_checks') or []
    trajectory = trial.get('trajectory', trial.get('messages', []))

    # Determine if task has failures
    has_failures = any(not ac.get('action_match', False) for ac in action_checks)
    header_class = 'task-header failed' if has_failures else 'task-header'

    # Check if any failures have the tool actually called (not "never_called")
    has_called_failures = False
    if has_failures:
        for ac in action_checks:
            if not ac.get('action_match', False):
                # Analyze this failure to determine category
                analysis = analyze_action_check(ac, trajectory)
                # Tool was called if there are any calls with the same name
                if analysis.get('all_tool_calls_with_name'):
                    has_called_failures = True
                    break

    # Count stats
    total_checks = len(action_checks)
    failed_checks = sum(1 for ac in action_checks if not ac.get('action_match', False))

    html = f'<div class="task-section" data-has-failures="{str(has_failures).lower()}" data-has-called-failures="{str(has_called_failures).lower()}" id="task-{index}">'

    # Header
    html += f'<div class="{header_class}">'
    html += f'<div class="task-title">Task #{index + 1}: {task_id}</div>'
    html += '<div style="display: flex; gap: 15px; align-items: center;">'

    if has_failures:
        html += f'<div class="task-badge">❌ {failed_checks}/{total_checks} Failed</div>'
    else:
        html += f'<div class="task-badge">✅ All Passed ({total_checks})</div>'

    html += '<span class="expand-icon">▼</span>'
    html += '</div>'
    html += '</div>'

    # Content
    html += '<div class="task-content">'
    html += render_task_details(trial)
    html += render_simulation_details(trial)
    html += render_action_checks(trial)
    html += '</div>'

    html += '</div>'

    return html


def generate_html_report(results_file: str, output_file: str = None):
    """Generate comprehensive HTML report from simulation results."""

    print(f"\n{'='*80}")
    print(f"GENERATING COMPREHENSIVE HTML REPORT")
    print(f"{'='*80}\n")
    print(f"Results File: {results_file}")

    # Load results
    with open(results_file, 'r') as f:
        results = json.load(f)

    # Support both 'trials' and 'simulations' format
    trials = results.get('trials', results.get('simulations', []))

    if not trials:
        print("❌ No trials found in results file!")
        return

    print(f"Found {len(trials)} trials")

    # Calculate overall statistics
    total_trials = len(trials)
    total_action_checks = 0
    total_failures = 0
    failures_by_action = defaultdict(int)
    tasks_with_failures = set()

    for trial in trials:
        reward_info = trial.get('reward_info', {})
        action_checks = reward_info.get('action_checks') or []
        total_action_checks += len(action_checks)

        for action_check in action_checks:
            if not action_check.get('action_match', False):
                total_failures += 1
                action_name = action_check['action']['name']
                failures_by_action[action_name] += 1
                tasks_with_failures.add(trial.get('task_id', 'unknown'))

    success_rate = (1 - total_failures / total_action_checks) * 100 if total_action_checks > 0 else 0

    # Build HTML content
    content = '<h1>Comprehensive Simulation Report</h1>'

    # Header Info
    content += '<div class="header-info">'
    content += f'<div class="info-item"><div class="info-label">Report Generated</div><div class="info-value">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div></div>'
    content += f'<div class="info-item"><div class="info-label">Results File</div><div class="info-value">{Path(results_file).name}</div></div>'
    content += '</div>'

    # Summary Statistics
    content += '<div class="summary-stats">'
    content += f'<div class="stat-card info"><div class="stat-value">{total_trials}</div><div class="stat-label">Total Trials</div></div>'
    content += f'<div class="stat-card info"><div class="stat-value">{total_action_checks}</div><div class="stat-label">Action Checks</div></div>'

    if total_failures > 0:
        content += f'<div class="stat-card error"><div class="stat-value">{total_failures}</div><div class="stat-label">Failed Checks</div></div>'
    else:
        content += f'<div class="stat-card success"><div class="stat-value">0</div><div class="stat-label">Failed Checks</div></div>'

    if success_rate >= 80:
        content += f'<div class="stat-card success"><div class="stat-value">{success_rate:.1f}%</div><div class="stat-label">Success Rate</div></div>'
    elif success_rate >= 50:
        content += f'<div class="stat-card warning"><div class="stat-value">{success_rate:.1f}%</div><div class="stat-label">Success Rate</div></div>'
    else:
        content += f'<div class="stat-card error"><div class="stat-value">{success_rate:.1f}%</div><div class="stat-label">Success Rate</div></div>'

    content += f'<div class="stat-card {"error" if tasks_with_failures else "success"}"><div class="stat-value">{len(tasks_with_failures)}</div><div class="stat-label">Tasks with Failures</div></div>'
    content += '</div>'

    # Failures by action type
    if failures_by_action:
        content += '<div style="margin: 20px 0; padding: 20px; background: #fff3cd; border-radius: 6px; border-left: 4px solid #ffc107;">'
        content += '<h3 style="margin-bottom: 15px;">Failures by Action Type</h3>'
        content += '<ul style="margin-left: 20px;">'
        for action_name, count in sorted(failures_by_action.items(), key=lambda x: x[1], reverse=True):
            content += f'<li><strong><code>{action_name}</code></strong>: {count} failure(s)</li>'
        content += '</ul>'
        content += '</div>'

    # Control buttons
    content += '<div class="controls">'
    content += '<button class="control-btn" id="toggle-all-btn" onclick="toggleAllTasks()">Collapse All</button>'
    content += '<button class="control-btn" onclick="showFailedOnly()">Show Failed Only</button>'
    content += '<button class="control-btn" onclick="showCalledWithDiff()">Show Called w/ Diff Only</button>'
    content += '<button class="control-btn" onclick="showAll()">Show All</button>'
    content += '<div class="task-counter" id="task-counter">Showing: Loading...</div>'
    content += '</div>'

    # Task sections
    print(f"\nGenerating task sections...")
    for i, trial in enumerate(trials):
        content += render_task_section(trial, i)
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{total_trials} tasks...")

    # Footer
    content += '<div class="footer">'
    content += f'Generated by tau2-enhanced | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    content += '</div>'

    # Generate final HTML
    html = HTML_TEMPLATE.replace('{content}', content)

    # Write to file
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"\n{'='*80}")
    print(f"✅ Report generated successfully!")
    print(f"📄 Output: {output_file}")
    print(f"{'='*80}\n")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate action failure analysis HTML report from simulation results",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'results_file',
        type=Path,
        help='Path to simulation results JSON file'
    )

    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        default=Path("analysis_results"),
        help='Base directory to save report (default: analysis_results/)'
    )

    parser.add_argument(
        '--output-file',
        help='Custom output filename (default: action_failure_report.html)',
        default=None
    )

    args = parser.parse_args()

    if not args.results_file.exists():
        print(f"❌ Error: File not found: {args.results_file}")
        sys.exit(1)

    # Create subfolder based on input filename (same as analyze_simple_logs.py)
    output_subdir = args.output_dir / args.results_file.stem
    output_subdir.mkdir(parents=True, exist_ok=True)

    # Determine output file path
    if args.output_file:
        output_path = output_subdir / args.output_file
    else:
        output_path = output_subdir / "action_failure_report.html"

    print(f"💾 Output will be saved to: {output_subdir}")

    try:
        generate_html_report(str(args.results_file), str(output_path))
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
