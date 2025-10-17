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
from collections import defaultdict

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


def create_deep_insights_report(analyzer, output_path, source_file):
    """Create comprehensive HTML report with deep insights."""

    # Analyze all aspects
    state_data, detailed_changes = analyzer.analyze_state_changes()
    context_data = analyzer.analyze_context_usage()
    metrics_data = analyzer.analyze_execution_metrics()
    failure_patterns = analyzer.analyze_failure_patterns()

    # Create visualizations
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
        </div>

        <script>
            var plotData = {fig.to_json()};
            Plotly.newPlot('visualizations', plotData.data, plotData.layout);
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
