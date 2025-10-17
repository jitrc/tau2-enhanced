#!/usr/bin/env python3
"""
Deep Insights Analysis for tau2-bench log files.

This script analyzes additional fields not included in the reduced logs:
- state_snapshots: State changes throughout execution
- context_usage_snapshots: Token usage and context window tracking
- execution_metrics: Aggregated execution statistics
- raw_data from messages: Full API responses

Generates HTML reports with visualizations for failure analysis and insights.
"""

import argparse
import json
from pathlib import Path
import sys
from datetime import datetime
from collections import defaultdict, Counter
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    print("Error: plotly is required. Install with: pip install plotly")
    sys.exit(1)


class DeepInsightsAnalyzer:
    """Analyzer for deep insights from full tau2-bench logs."""

    def __init__(self, log_data):
        self.log_data = log_data
        self.simulations = log_data.get('simulations', [])

    def analyze_state_changes(self):
        """Analyze state changes across simulations."""
        state_data = []
        detailed_changes = []

        for sim in self.simulations:
            sim_id = f"Task {sim.get('task_id', 'N/A')} | Trial {sim.get('trial', 'N/A')}"
            success = sim.get('reward', 0) > 0

            snapshots = sim.get('state_snapshots', [])
            state_change_snapshots = [s for s in snapshots if s.get('state_changed', False)]

            # Collect detailed state change info
            for snapshot in state_change_snapshots:
                db_diff = snapshot.get('db_diff', {})

                change_detail = {
                    'sim_id': sim_id,
                    'success': success,
                    'step_idx': snapshot.get('step_idx', 0),
                    'triggered_by': snapshot.get('triggered_by', 'unknown'),
                    'added': list(db_diff.get('added', {}).keys()) if db_diff.get('added') else [],
                    'modified': list(db_diff.get('modified', {}).keys()) if db_diff.get('modified') else [],
                    'removed': list(db_diff.get('removed', {}).keys()) if db_diff.get('removed') else []
                }
                detailed_changes.append(change_detail)

            state_data.append({
                'sim_id': sim_id,
                'success': success,
                'state_changes': len(state_change_snapshots),
                'total_snapshots': len(snapshots),
                'reward': sim.get('reward', 0)
            })

        return state_data, detailed_changes

    def analyze_context_usage(self):
        """Analyze context window usage patterns."""
        context_data = []

        for sim in self.simulations:
            sim_id = f"Task {sim.get('task_id', 'N/A')} | Trial {sim.get('trial', 'N/A')}"
            success = sim.get('reward', 0) > 0

            snapshots = sim.get('context_usage_snapshots', [])
            if snapshots:
                total_prompt_tokens = sum(s.get('prompt_tokens', 0) for s in snapshots)
                total_completion_tokens = sum(s.get('completion_tokens', 0) for s in snapshots)
                max_tokens = max((s.get('total_tokens', 0) for s in snapshots), default=0)

                context_data.append({
                    'sim_id': sim_id,
                    'success': success,
                    'total_prompt_tokens': total_prompt_tokens,
                    'total_completion_tokens': total_completion_tokens,
                    'total_tokens': total_prompt_tokens + total_completion_tokens,
                    'max_tokens': max_tokens,
                    'num_snapshots': len(snapshots)
                })

        return context_data

    def analyze_execution_metrics(self):
        """Analyze execution metrics."""
        metrics_data = []

        for sim in self.simulations:
            sim_id = f"Task {sim.get('task_id', 'N/A')} | Trial {sim.get('trial', 'N/A')}"
            success = sim.get('reward', 0) > 0

            metrics = sim.get('execution_metrics', {})

            metrics_data.append({
                'sim_id': sim_id,
                'success': success,
                'total_tool_calls': metrics.get('total_tool_calls', 0),
                'failed_tool_calls': metrics.get('failed_tool_calls', 0),
                'avg_execution_time_ms': metrics.get('average_execution_time_ms', 0),
                'unique_tools': len(metrics.get('unique_tools_used', [])),
                'state_changes': metrics.get('state_changes', 0),
                'total_tokens': metrics.get('total_tokens', 0),
                'context_warnings': metrics.get('context_window_warnings', 0)
            })

        return metrics_data

    def analyze_failure_patterns(self):
        """Analyze patterns in failed simulations."""
        failed_sims = [s for s in self.simulations if s.get('reward', 0) <= 0]
        success_sims = [s for s in self.simulations if s.get('reward', 0) > 0]

        def get_avg_metrics(sims):
            if not sims:
                return {}

            return {
                'avg_tool_calls': sum(s.get('execution_metrics', {}).get('total_tool_calls', 0) for s in sims) / len(sims),
                'avg_failed_calls': sum(s.get('execution_metrics', {}).get('failed_tool_calls', 0) for s in sims) / len(sims),
                'avg_tokens': sum(s.get('execution_metrics', {}).get('total_tokens', 0) for s in sims) / len(sims),
                'avg_state_changes': sum(len(s.get('state_snapshots', [])) for s in sims) / len(sims),
                'avg_duration': sum(s.get('duration', 0) for s in sims) / len(sims),
            }

        return {
            'failed': get_avg_metrics(failed_sims),
            'success': get_avg_metrics(success_sims),
            'failed_count': len(failed_sims),
            'success_count': len(success_sims)
        }

    def analyze_action_checks(self):
        """Analyze detailed validation failures from action checks."""
        action_failures = []

        for sim in self.simulations:
            sim_id = f"Task {sim.get('task_id', 'N/A')} | Trial {sim.get('trial', 'N/A')}"
            success = sim.get('reward', 0) > 0

            # Look through messages for validation errors
            messages = sim.get('messages', [])
            for idx, msg in enumerate(messages):
                # Check both error formats: tool_call_status='error' or error=True
                is_error = (msg.get('role') == 'tool' and
                           (msg.get('tool_call_status') == 'error' or msg.get('error') is True))

                if is_error:
                    content = str(msg.get('content', ''))
                    tool_name = msg.get('tool_name', 'unknown')

                    # Try to extract tool name from requestor field if not present
                    if tool_name == 'unknown' and msg.get('requestor'):
                        tool_name = msg.get('requestor')

                    # Extract validation error details
                    validation_match = re.search(r'ValidationError: (.+)', content)
                    error_match = re.search(r'Error: (.+)', content)

                    if validation_match:
                        error_type = 'ValidationError'
                        error_detail = validation_match.group(1)
                    elif error_match:
                        error_type = 'Error'
                        error_detail = error_match.group(1)
                    else:
                        error_type = 'Error'
                        error_detail = content[:200]

                    action_failures.append({
                        'sim_id': sim_id,
                        'success': success,
                        'tool_name': tool_name,
                        'error_type': error_type,
                        'error_detail': error_detail,
                        'step_idx': msg.get('step_idx', idx)
                    })

        return action_failures

    def analyze_tool_timeline(self):
        """Create timeline data for tool call execution flow."""
        timeline_data = []

        for sim in self.simulations:
            sim_id = f"Task {sim.get('task_id', 'N/A')} | Trial {sim.get('trial', 'N/A')}"
            success = sim.get('reward', 0) > 0

            messages = sim.get('messages', [])
            tool_calls = [m for m in messages if m.get('role') == 'tool']

            for idx, tool_call in enumerate(tool_calls):
                timeline_data.append({
                    'sim_id': sim_id,
                    'success': success,
                    'step_idx': idx,
                    'tool_name': tool_call.get('tool_name', 'unknown'),
                    'status': tool_call.get('tool_call_status', 'unknown'),
                    'execution_time_ms': tool_call.get('execution_time_ms', 0)
                })

        return timeline_data

    def analyze_root_causes(self):
        """Categorize and identify root causes of failures."""
        root_causes = defaultdict(list)

        for sim in self.simulations:
            if sim.get('reward', 0) > 0:
                continue  # Only analyze failures

            sim_id = f"Task {sim.get('task_id', 'N/A')} | Trial {sim.get('trial', 'N/A')}"

            # Categorize by various failure indicators
            messages = sim.get('messages', [])
            metrics = sim.get('execution_metrics', {})

            # Check for error patterns - support both error formats
            error_msgs = [m for m in messages if m.get('role') == 'tool' and
                         (m.get('tool_call_status') == 'error' or m.get('error') is True)]
            timeout_errors = [m for m in error_msgs if 'timeout' in str(m.get('content', '')).lower()]
            validation_errors = [m for m in error_msgs if 'validation' in str(m.get('content', '')).lower()]

            # Categorize
            if timeout_errors:
                root_causes['Timeout Errors'].append(sim_id)
            elif validation_errors:
                root_causes['Validation Errors'].append(sim_id)
            elif len(error_msgs) > 5:
                root_causes['High Error Rate'].append(sim_id)
            elif metrics.get('total_tool_calls', 0) < 5:
                root_causes['Insufficient Actions'].append(sim_id)
            elif metrics.get('state_changes', 0) == 0:
                root_causes['No State Changes'].append(sim_id)
            else:
                root_causes['Other/Complex'].append(sim_id)

        return dict(root_causes)

    def analyze_cost(self):
        """Analyze token costs broken down by success/failure."""
        # Pricing per 1M tokens (example rates - adjust as needed)
        PROMPT_COST_PER_1M = 3.0  # $3 per 1M prompt tokens
        COMPLETION_COST_PER_1M = 15.0  # $15 per 1M completion tokens

        cost_data = {
            'success': {'prompt_tokens': 0, 'completion_tokens': 0, 'count': 0},
            'failed': {'prompt_tokens': 0, 'completion_tokens': 0, 'count': 0}
        }

        for sim in self.simulations:
            success = sim.get('reward', 0) > 0
            key = 'success' if success else 'failed'

            snapshots = sim.get('context_usage_snapshots', [])
            if snapshots:
                prompt_tokens = sum(s.get('prompt_tokens', 0) for s in snapshots)
                completion_tokens = sum(s.get('completion_tokens', 0) for s in snapshots)

                cost_data[key]['prompt_tokens'] += prompt_tokens
                cost_data[key]['completion_tokens'] += completion_tokens
                cost_data[key]['count'] += 1

        # Calculate costs
        for key in cost_data:
            data = cost_data[key]
            data['prompt_cost'] = (data['prompt_tokens'] / 1_000_000) * PROMPT_COST_PER_1M
            data['completion_cost'] = (data['completion_tokens'] / 1_000_000) * COMPLETION_COST_PER_1M
            data['total_cost'] = data['prompt_cost'] + data['completion_cost']
            data['avg_cost_per_sim'] = data['total_cost'] / data['count'] if data['count'] > 0 else 0

        return cost_data

    def analyze_error_clustering(self):
        """Cluster and group common error patterns."""
        error_patterns = Counter()
        error_details = defaultdict(list)

        for sim in self.simulations:
            sim_id = f"Task {sim.get('task_id', 'N/A')} | Trial {sim.get('trial', 'N/A')}"
            success = sim.get('reward', 0) > 0

            messages = sim.get('messages', [])
            for msg in messages:
                # Check both error formats
                is_error = (msg.get('role') == 'tool' and
                           (msg.get('tool_call_status') == 'error' or msg.get('error') is True))

                if is_error:
                    content = str(msg.get('content', ''))
                    tool_name = msg.get('tool_name', 'unknown')

                    # Try to extract tool name from requestor field if not present
                    if tool_name == 'unknown' and msg.get('requestor'):
                        tool_name = msg.get('requestor')

                    # Extract error type and specific message
                    if 'ValidationError' in content:
                        error_type = 'ValidationError'
                    elif 'timeout' in content.lower():
                        error_type = 'TimeoutError'
                    elif 'permission' in content.lower():
                        error_type = 'PermissionError'
                    elif 'not found' in content.lower():
                        error_type = 'NotFoundError'
                    elif 'Error:' in content:
                        # Extract specific error message after "Error:"
                        error_match = re.search(r'Error: (.+?)(?:\n|$)', content)
                        if error_match:
                            error_msg = error_match.group(1).strip()
                            # Use the specific error message as the type
                            error_type = error_msg[:50]  # Truncate if too long
                        else:
                            error_type = 'GenericError'
                    else:
                        # Try to extract error class
                        match = re.search(r'(\w+Error)', content)
                        error_type = match.group(1) if match else 'GenericError'

                    pattern_key = f"{tool_name}: {error_type}"
                    error_patterns[pattern_key] += 1
                    error_details[pattern_key].append({
                        'sim_id': sim_id,
                        'success': success,
                        'sample': content[:150]
                    })

        return error_patterns, error_details


def create_deep_insights_report(analyzer, output_path, source_file):
    """Create comprehensive HTML report with deep insights."""

    # Analyze all aspects
    state_data, detailed_changes = analyzer.analyze_state_changes()
    context_data = analyzer.analyze_context_usage()
    metrics_data = analyzer.analyze_execution_metrics()
    failure_patterns = analyzer.analyze_failure_patterns()

    # New analyses
    action_failures = analyzer.analyze_action_checks()
    timeline_data = analyzer.analyze_tool_timeline()
    root_causes = analyzer.analyze_root_causes()
    cost_data = analyzer.analyze_cost()
    error_patterns, error_details = analyzer.analyze_error_clustering()

    # Create main visualizations
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'State Changes per Simulation',
            'Context Token Usage',
            'Tool Calls vs Success Rate',
            'Execution Time Distribution',
            'Failure Pattern Comparison',
            'Context Warnings by Success'
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "histogram"}],
            [{"type": "bar"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # Create additional figures for new analyses
    # Figure 2: Root Cause Analysis
    fig_root_cause = go.Figure()
    if root_causes:
        fig_root_cause.add_trace(go.Bar(
            x=list(root_causes.keys()),
            y=[len(v) for v in root_causes.values()],
            marker_color='#e74c3c',
            text=[len(v) for v in root_causes.values()],
            textposition='auto',
        ))
        fig_root_cause.update_layout(
            title='Failure Root Cause Distribution',
            xaxis_title='Root Cause Category',
            yaxis_title='Number of Failed Simulations',
            height=400
        )

    # Figure 3: Cost Analysis
    fig_cost = go.Figure()
    fig_cost.add_trace(go.Bar(
        name='Success',
        x=['Prompt Cost', 'Completion Cost', 'Total Cost'],
        y=[cost_data['success']['prompt_cost'],
           cost_data['success']['completion_cost'],
           cost_data['success']['total_cost']],
        marker_color='green'
    ))
    fig_cost.add_trace(go.Bar(
        name='Failed',
        x=['Prompt Cost', 'Completion Cost', 'Total Cost'],
        y=[cost_data['failed']['prompt_cost'],
           cost_data['failed']['completion_cost'],
           cost_data['failed']['total_cost']],
        marker_color='red'
    ))
    fig_cost.update_layout(
        title='Cost Analysis: Success vs Failed Simulations',
        yaxis_title='Cost ($)',
        barmode='group',
        height=400
    )

    # Figure 4: Error Pattern Clustering
    fig_errors = go.Figure()
    if error_patterns:
        top_errors = error_patterns.most_common(10)
        fig_errors.add_trace(go.Bar(
            x=[count for _, count in top_errors],
            y=[pattern for pattern, _ in top_errors],
            orientation='h',
            marker_color='#e67e22',
            text=[count for _, count in top_errors],
            textposition='auto'
        ))
        fig_errors.update_layout(
            title='Top 10 Error Patterns',
            xaxis_title='Occurrence Count',
            yaxis_title='Error Pattern',
            height=500
        )

    # Figure 5: Tool Timeline (sample from first few simulations)
    fig_timeline = go.Figure()
    sample_sims = list(set([t['sim_id'] for t in timeline_data[:100]]))[:3]  # First 3 sims
    for sim_id in sample_sims:
        sim_timeline = [t for t in timeline_data if t['sim_id'] == sim_id]
        fig_timeline.add_trace(go.Scatter(
            x=[t['step_idx'] for t in sim_timeline],
            y=[t['execution_time_ms'] for t in sim_timeline],
            mode='lines+markers',
            name=sim_id,
            text=[t['tool_name'] for t in sim_timeline],
            hovertemplate='<b>%{text}</b><br>Step: %{x}<br>Time: %{y}ms<extra></extra>'
        ))
    fig_timeline.update_layout(
        title='Tool Call Timeline (Sample)',
        xaxis_title='Step Index',
        yaxis_title='Execution Time (ms)',
        height=400
    )

    # 1. State Changes
    success_states = [d for d in state_data if d['success']]
    failed_states = [d for d in state_data if not d['success']]

    fig.add_trace(
        go.Bar(
            x=[d['sim_id'] for d in success_states],
            y=[d['state_changes'] for d in success_states],
            name='Success',
            marker_color='green'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=[d['sim_id'] for d in failed_states],
            y=[d['state_changes'] for d in failed_states],
            name='Failed',
            marker_color='red'
        ),
        row=1, col=1
    )

    # 2. Context Usage
    fig.add_trace(
        go.Scatter(
            x=[d['total_prompt_tokens'] for d in context_data],
            y=[d['total_completion_tokens'] for d in context_data],
            mode='markers',
            marker=dict(
                size=10,
                color=['green' if d['success'] else 'red' for d in context_data],
                line=dict(width=1, color='white')
            ),
            text=[d['sim_id'] for d in context_data],
            name='Token Usage'
        ),
        row=1, col=2
    )

    # 3. Tool Calls vs Success
    fig.add_trace(
        go.Scatter(
            x=[d['total_tool_calls'] for d in metrics_data],
            y=[1 if d['success'] else 0 for d in metrics_data],
            mode='markers',
            marker=dict(
                size=[d['failed_tool_calls'] * 5 + 5 for d in metrics_data],
                color=[d['failed_tool_calls'] for d in metrics_data],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Failed<br>Calls", x=0.46)
            ),
            text=[d['sim_id'] for d in metrics_data],
            name='Success vs Tools'
        ),
        row=2, col=1
    )

    # 4. Execution Time Distribution
    exec_times = [d['avg_execution_time_ms'] for d in metrics_data if d['avg_execution_time_ms'] > 0]
    fig.add_trace(
        go.Histogram(
            x=exec_times,
            nbinsx=20,
            name='Execution Time',
            marker_color='#667eea'
        ),
        row=2, col=2
    )

    # 5. Failure Pattern Comparison
    categories = ['Tool Calls', 'Failed Calls', 'State Changes', 'Duration (s)']
    failed_vals = [
        failure_patterns['failed'].get('avg_tool_calls', 0),
        failure_patterns['failed'].get('avg_failed_calls', 0),
        failure_patterns['failed'].get('avg_state_changes', 0),
        failure_patterns['failed'].get('avg_duration', 0)
    ]
    success_vals = [
        failure_patterns['success'].get('avg_tool_calls', 0),
        failure_patterns['success'].get('avg_failed_calls', 0),
        failure_patterns['success'].get('avg_state_changes', 0),
        failure_patterns['success'].get('avg_duration', 0)
    ]

    fig.add_trace(
        go.Bar(x=categories, y=failed_vals, name='Failed', marker_color='red'),
        row=3, col=1
    )
    fig.add_trace(
        go.Bar(x=categories, y=success_vals, name='Success', marker_color='green'),
        row=3, col=1
    )

    # 6. Context Warnings
    warning_data = defaultdict(int)
    for d in metrics_data:
        key = 'Success' if d['success'] else 'Failed'
        warning_data[key] += d['context_warnings']

    fig.add_trace(
        go.Bar(
            x=list(warning_data.keys()),
            y=list(warning_data.values()),
            marker_color=['green', 'red'],
            name='Context Warnings'
        ),
        row=3, col=2
    )

    # Update layout
    fig.update_layout(
        height=1200,
        title_text=f"Deep Insights Analysis - {source_file}",
        showlegend=True,
        title_font_size=20
    )

    # Update axes
    fig.update_xaxes(title_text="Simulation", row=1, col=1)
    fig.update_yaxes(title_text="State Changes", row=1, col=1)

    fig.update_xaxes(title_text="Prompt Tokens", row=1, col=2)
    fig.update_yaxes(title_text="Completion Tokens", row=1, col=2)

    fig.update_xaxes(title_text="Total Tool Calls", row=2, col=1)
    fig.update_yaxes(title_text="Success (1) / Failed (0)", row=2, col=1)

    fig.update_xaxes(title_text="Execution Time (ms)", row=2, col=2)
    fig.update_yaxes(title_text="Count", row=2, col=2)

    fig.update_xaxes(title_text="Metric", row=3, col=1)
    fig.update_yaxes(title_text="Average Value", row=3, col=1)

    fig.update_xaxes(title_text="Success Status", row=3, col=2)
    fig.update_yaxes(title_text="Total Warnings", row=3, col=2)

    # Create HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Deep Insights Analysis Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f7fa;
            }}
            .header {{
                text-align: center;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0 0 10px 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            .header .subtitle {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            .content {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .metric-label {{
                font-size: 0.9em;
                opacity: 0.9;
            }}
            .insights-section {{
                margin: 30px 0;
            }}
            .insight-title {{
                font-size: 1.5em;
                font-weight: 600;
                color: #2c3e50;
                margin: 20px 0 15px 0;
                padding-left: 15px;
                border-left: 4px solid #667eea;
            }}
            .insight-text {{
                padding: 15px;
                background: #f8f9ff;
                border-radius: 8px;
                margin: 10px 0;
                line-height: 1.6;
            }}
            .state-changes-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            .state-changes-table th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }}
            .state-changes-table td {{
                padding: 10px 12px;
                border-bottom: 1px solid #e1e8ed;
            }}
            .state-changes-table tr:hover {{
                background: #f8f9ff;
            }}
            .success-row {{
                background: #f0fdf4;
            }}
            .failed-row {{
                background: #fef2f2;
            }}
            .change-badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.85em;
                margin: 2px;
            }}
            .added-badge {{
                background: #d1fae5;
                color: #065f46;
            }}
            .modified-badge {{
                background: #fef3c7;
                color: #92400e;
            }}
            .removed-badge {{
                background: #fee2e2;
                color: #991b1b;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔬 Deep Insights Analysis Report</h1>
            <div class="subtitle">
                Advanced analysis of state changes, context usage, and failure patterns<br>
                Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}<br>
                Source: <strong>{source_file}</strong>
            </div>
        </div>

        <div class="content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{len(state_data)}</div>
                    <div class="metric-label">Total Simulations</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{failure_patterns['success_count']}</div>
                    <div class="metric-label">Successful</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{failure_patterns['failed_count']}</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{sum(d['total_tokens'] for d in context_data):,}</div>
                    <div class="metric-label">Total Tokens Used</div>
                </div>
            </div>

            <div class="insights-section">
                <div class="insight-title">🎯 Key Insights</div>

                <div class="insight-text">
                    <strong>State Change Patterns:</strong><br>
                    • Failed simulations average {failure_patterns['failed'].get('avg_state_changes', 0):.1f} state snapshots<br>
                    • Successful simulations average {failure_patterns['success'].get('avg_state_changes', 0):.1f} state snapshots<br>
                    • Difference: {abs(failure_patterns['failed'].get('avg_state_changes', 0) - failure_patterns['success'].get('avg_state_changes', 0)):.1f} fewer/more snapshots in failures
                </div>

                <div class="insight-text">
                    <strong>Tool Usage Patterns:</strong><br>
                    • Failed simulations: {failure_patterns['failed'].get('avg_tool_calls', 0):.1f} avg tool calls, {failure_patterns['failed'].get('avg_failed_calls', 0):.1f} avg failures<br>
                    • Successful simulations: {failure_patterns['success'].get('avg_tool_calls', 0):.1f} avg tool calls, {failure_patterns['success'].get('avg_failed_calls', 0):.1f} avg failures<br>
                    • Failure rate impact: {(failure_patterns['failed'].get('avg_failed_calls', 0) / max(failure_patterns['failed'].get('avg_tool_calls', 1), 1) * 100):.1f}% in failed vs {(failure_patterns['success'].get('avg_failed_calls', 0) / max(failure_patterns['success'].get('avg_tool_calls', 1), 1) * 100):.1f}% in successful
                </div>

                <div class="insight-text">
                    <strong>Context Usage:</strong><br>
                    • Average tokens per simulation: {sum(d['total_tokens'] for d in context_data) / len(context_data) if context_data else 0:,.0f}<br>
                    • Total context warnings: {sum(d['context_warnings'] for d in metrics_data)}<br>
                    • Max tokens in single simulation: {max((d['total_tokens'] for d in context_data), default=0):,}
                </div>

                <div class="insight-text">
                    <strong>Execution Time:</strong><br>
                    • Failed simulations duration: {failure_patterns['failed'].get('avg_duration', 0):.1f}s<br>
                    • Successful simulations duration: {failure_patterns['success'].get('avg_duration', 0):.1f}s<br>
                    • Time difference: {abs(failure_patterns['failed'].get('avg_duration', 0) - failure_patterns['success'].get('avg_duration', 0)):.1f}s
                </div>
            </div>

            <div class="insights-section">
                <div class="insight-title">🔄 Detailed State Changes</div>
                <p style="color: #64748b; margin-bottom: 15px;">
                    All database modifications tracked during execution. Failed simulations are highlighted in red.
                </p>

                <table class="state-changes-table">
                    <thead>
                        <tr>
                            <th>Simulation</th>
                            <th>Success</th>
                            <th>Step</th>
                            <th>Triggered By</th>
                            <th>Changes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr class="{'success-row' if change['success'] else 'failed-row'}">
                            <td>{change['sim_id']}</td>
                            <td>{'✅ Success' if change['success'] else '❌ Failed'}</td>
                            <td>{change['step_idx']}</td>
                            <td><code>{change['triggered_by']}</code></td>
                            <td>
                                {''.join([f'<span class="change-badge added-badge">+{item}</span>' for item in change['added']])}
                                {''.join([f'<span class="change-badge modified-badge">~{item}</span>' for item in change['modified']])}
                                {''.join([f'<span class="change-badge removed-badge">-{item}</span>' for item in change['removed']])}
                                {' <em style="color: #94a3b8;">No changes</em>' if not change['added'] and not change['modified'] and not change['removed'] else ''}
                            </td>
                        </tr>
                        ''' for change in detailed_changes[:50]])}  <!-- Limit to first 50 for performance -->
                    </tbody>
                </table>
                {f'<p style="color: #64748b; font-style: italic;">Showing first 50 of {len(detailed_changes)} total state changes.</p>' if len(detailed_changes) > 50 else ''}
            </div>

            <div id="visualizations"></div>

            <!-- NEW SECTIONS -->

            <div class="insights-section">
                <div class="insight-title">🚨 Action Check Failures</div>
                <p style="color: #64748b; margin-bottom: 15px;">
                    Detailed validation errors and tool execution failures.
                </p>

                <table class="state-changes-table">
                    <thead>
                        <tr>
                            <th>Simulation</th>
                            <th>Success</th>
                            <th>Step</th>
                            <th>Tool</th>
                            <th>Error Type</th>
                            <th>Error Detail</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr class="{'success-row' if fail['success'] else 'failed-row'}">
                            <td>{fail['sim_id']}</td>
                            <td>{'✅' if fail['success'] else '❌'}</td>
                            <td>{fail['step_idx']}</td>
                            <td><code>{fail['tool_name']}</code></td>
                            <td><span class="change-badge removed-badge">{fail['error_type']}</span></td>
                            <td style="font-size: 0.85em; max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{fail['error_detail']}</td>
                        </tr>
                        ''' for fail in action_failures[:50]])}  <!-- Limit to first 50 -->
                    </tbody>
                </table>
                {f'<p style="color: #64748b; font-style: italic;">Showing first 50 of {len(action_failures)} total action failures.</p>' if len(action_failures) > 50 else ''}
            </div>

            <div class="insights-section">
                <div class="insight-title">⚡ Tool Call Timeline</div>
                <div id="timeline-chart"></div>
            </div>

            <div class="insights-section">
                <div class="insight-title">🎯 Failure Root Cause Analysis</div>
                <div id="root-cause-chart"></div>

                <div style="margin-top: 20px;">
                    <strong>Root Cause Breakdown:</strong>
                    {''.join([f'<div class="insight-text"><strong>{category}:</strong> {len(sims)} simulation(s) - {", ".join(sims[:3])}{"..." if len(sims) > 3 else ""}</div>' for category, sims in root_causes.items()])}
                </div>
            </div>

            <div class="insights-section">
                <div class="insight-title">💰 Cost Analysis</div>
                <div id="cost-chart"></div>

                <div class="metrics-grid" style="margin-top: 20px;">
                    <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                        <div class="metric-value">${cost_data['success']['avg_cost_per_sim']:.4f}</div>
                        <div class="metric-label">Avg Cost per Successful Sim</div>
                    </div>
                    <div class="metric-card" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
                        <div class="metric-value">${cost_data['failed']['avg_cost_per_sim']:.4f}</div>
                        <div class="metric-label">Avg Cost per Failed Sim</div>
                    </div>
                    <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                        <div class="metric-value">${cost_data['success']['total_cost'] + cost_data['failed']['total_cost']:.2f}</div>
                        <div class="metric-label">Total Execution Cost</div>
                    </div>
                    <div class="metric-card" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);">
                        <div class="metric-value">{sum(d['total_tokens'] for d in context_data):,}</div>
                        <div class="metric-label">Total Tokens</div>
                    </div>
                </div>
            </div>

            <div class="insights-section">
                <div class="insight-title">🔍 Error Pattern Clustering</div>
                <div id="error-chart"></div>

                <div style="margin-top: 20px;">
                    <strong>Most Common Error Patterns:</strong>
                    {''.join([f'''<div class="insight-text">
                        <strong>{pattern}</strong>: {count} occurrence(s)<br>
                        <em style="color: #64748b; font-size: 0.9em;">Sample: {error_details[pattern][0]['sample'] if error_details[pattern] else 'N/A'}</em>
                    </div>''' for pattern, count in (error_patterns.most_common(5) if error_patterns else [])])}
                </div>
            </div>
        </div>

        <script>
            var plotData = {fig.to_json()};
            Plotly.newPlot('visualizations', plotData.data, plotData.layout);

            // Render additional charts
            var timelineData = {fig_timeline.to_json()};
            Plotly.newPlot('timeline-chart', timelineData.data, timelineData.layout);

            var rootCauseData = {fig_root_cause.to_json()};
            Plotly.newPlot('root-cause-chart', rootCauseData.data, rootCauseData.layout);

            var costData = {fig_cost.to_json()};
            Plotly.newPlot('cost-chart', costData.data, costData.layout);

            var errorData = {fig_errors.to_json()};
            Plotly.newPlot('error-chart', errorData.data, errorData.layout);
        </script>
    </body>
    </html>
    """

    with open(output_path, 'w') as f:
        f.write(html_content)

    print(f"✅ Deep insights report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze deep insights from full tau2-bench log files"
    )
    parser.add_argument(
        "log_file",
        type=Path,
        help="Path to the full (non-reduced) JSON log file"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output HTML file path. If not specified, uses '<log_file>_deep_insights.html'"
    )

    args = parser.parse_args()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = args.log_file.parent / f"{args.log_file.stem}_deep_insights.html"

    print(f"📁 Loading logs from: {args.log_file}")

    try:
        with args.log_file.open('r') as f:
            data = json.load(f)
        print(f"  ✅ Successfully loaded log file")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error loading log file: {e}")
        return

    # Create analyzer
    analyzer = DeepInsightsAnalyzer(data)

    print(f"🔬 Analyzing {len(analyzer.simulations)} simulations...")

    # Generate report
    create_deep_insights_report(analyzer, output_path, args.log_file.name)

    print(f"\n🎉 Analysis complete!")
    print(f"📊 Open the report: {output_path}")


if __name__ == "__main__":
    main()
