import json
"""
Visualization tools for the simplified log format.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Optional

from .analyzer import LogAnalyzer


class LogVisualizer:
    """Creates visualizations from LogAnalyzer results."""

    def __init__(self, analyzer: LogAnalyzer):
        """
        Initialize with a LogAnalyzer instance.

        Args:
            analyzer: An instance of LogAnalyzer containing processed log data.
        """
        self.analyzer = analyzer

    def create_summary_dashboard(self, include_task_success=True) -> go.Figure:
        """
        Create a dashboard summarizing overall tool performance.

        Returns:
            A Plotly Figure object.
        """
        summary = self.analyzer.get_summary_metrics()
        tool_perf = self.analyzer.get_tool_performance()

        if include_task_success:
            # Full dashboard with both task and tool success rates
            fig = make_subplots(
                rows=2,
                cols=2,
                specs=[
                    [{"type": "indicator"}, {"type": "indicator"}],
                    [{"type": "bar"}, {"type": "bar"}]
                ],
                subplot_titles=("Task Success Rate", "Tool Success Rate", "Tool Success Rates", "Tool Execution Times")
            )

            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=summary.get('task_success_rate', 0) * 100,
                    title={'text': "Task Success %"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#4A90E2"},
                        'steps': [
                            {'range': [0, 40], 'color': "#FFF0F0"},
                            {'range': [40, 70], 'color': "#FFF8E7"},
                            {'range': [70, 100], 'color': "#F0FFF4"}
                        ],
                        'threshold': {
                            'line': {'color': "#E74C3C", 'width': 2},
                            'thickness': 0.75,
                            'value': 80
                        }
                    },
                    domain={'x': [0, 1], 'y': [0, 1]}
                ),
                row=1, col=1
            )

            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=summary.get('tool_success_rate', 0) * 100,
                    title={'text': "Tool Success %"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#4A90E2"},
                        'steps': [
                            {'range': [0, 40], 'color': "#FFF0F0"},
                            {'range': [40, 70], 'color': "#FFF8E7"},
                            {'range': [70, 100], 'color': "#F0FFF4"}
                        ],
                        'threshold': {
                            'line': {'color': "#E74C3C", 'width': 2},
                            'thickness': 0.75,
                            'value': 80
                        }
                    },
                ),
                row=1, col=2
            )
        else:
            # Tool-focused dashboard without task success rate
            fig = make_subplots(
                rows=2,
                cols=2,
                specs=[
                    [{"type": "indicator"}, {"type": "indicator"}],
                    [{"type": "bar"}, {"type": "bar"}]
                ],
                subplot_titles=("Tool Success Rate", "Total Success", "Tool Success Rates", "Tool Execution Times")
            )

            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=summary.get('tool_success_rate', 0) * 100,
                    title={'text': "Tool Success %"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#4A90E2"},
                        'steps': [
                            {'range': [0, 40], 'color': "#FFF0F0"},
                            {'range': [40, 70], 'color': "#FFF8E7"},
                            {'range': [70, 100], 'color': "#F0FFF4"}
                        ],
                        'threshold': {
                            'line': {'color': "#E74C3C", 'width': 2},
                            'thickness': 0.75,
                            'value': 80
                        }
                    },
                ),
                row=1, col=1
            )

            # Calculate total success rate combining both task and tool success
            task_success = summary.get('task_success_rate', 0) * 100
            tool_success = summary.get('tool_success_rate', 0) * 100
            total_success = (task_success + tool_success) / 2  # Average of both

            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=total_success,
                    title={'text': "Overall Success %"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#4A90E2"},
                        'steps': [
                            {'range': [0, 40], 'color': "#FFF0F0"},
                            {'range': [40, 70], 'color': "#FFF8E7"},
                            {'range': [70, 100], 'color': "#F0FFF4"}
                        ],
                        'threshold': {
                            'line': {'color': "#E74C3C", 'width': 2},
                            'thickness': 0.75,
                            'value': 80
                        }
                    },
                ),
                row=1, col=2
            )

        if not tool_perf.empty:
            fig.add_trace(
                go.Bar(
                    x=tool_perf['tool_name'],
                    y=tool_perf['success_rate'],
                    name='Success Rate',
                    marker_color='green',
                    text=[f"{rate:.1%}" for rate in tool_perf['success_rate']],
                    textposition='outside'
                ),
                row=2, col=1
            )
            fig.add_trace(
                go.Bar(
                    x=tool_perf['tool_name'],
                    y=tool_perf['avg_execution_time'] * 1000,  # Convert to ms
                    name='Avg. Time (ms)',
                    marker_color='blue',
                    text=[f"{time*1000:.2f}ms" for time in tool_perf['avg_execution_time']],
                    textposition='outside'
                ),
                row=2, col=2
            )

        fig.update_layout(
            title_text="Execution Summary Dashboard",
            height=800
        )

        # Update axes labels for the separated plots
        fig.update_xaxes(title_text="Tools", row=2, col=1)
        fig.update_yaxes(title_text="Success Rate", row=2, col=1, range=[0, 1.1])
        fig.update_xaxes(title_text="Tools", row=2, col=2)
        fig.update_yaxes(title_text="Execution Time (ms)", row=2, col=2)

        return fig

    def create_failure_analysis_plot(self) -> go.Figure:
        """
        Create a comprehensive failure analysis dashboard with multiple views.

        Returns:
            A Plotly Figure object with professional failure analysis charts.
        """
        failures = self.analyzer.get_failure_analysis()
        if failures.empty:
            return go.Figure().update_layout(
                title="✅ No Failures Recorded - All Tool Calls Successful",
                annotations=[
                    dict(
                        text="🎉 Excellent! All tool calls completed successfully without any errors.",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, xanchor='center', yanchor='middle',
                        showarrow=False,
                        font=dict(size=16, color="green")
                    )
                ]
            )

        # Determine subplot titles based on available data
        subplot2_title = "Failure Rate vs Execution Time" if 'avg_execution_time' in failures.columns else "Failure Rate vs Error Count"

        # Create comprehensive failure analysis dashboard
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "table"}]
            ],
            subplot_titles=(
                "Failure Count by Tool",
                subplot2_title,
                "Error Types Distribution",
                "Failure Details Summary"
            ),
            row_heights=[0.6, 0.4]
        )

        # 1. Failure count by tool (top-left)
        tool_failures = failures.groupby('tool_name')['count'].sum().sort_values(ascending=True)
        fig.add_trace(
            go.Bar(
                y=tool_failures.index,
                x=tool_failures.values,
                orientation='h',
                name='Failure Count',
                marker_color='crimson',
                text=tool_failures.values,
                textposition='outside'
            ),
            row=1, col=1
        )

        # 2. Failure rate vs failure count scatter (top-right)
        # Note: avg_execution_time may not be available for action check failures
        if 'avg_execution_time' in failures.columns:
            x_data = failures['avg_execution_time'] * 1000  # Convert to ms
            x_title = 'Avg Execution Time (ms)'
            hover_template = (
                '<b>%{text}</b><br>' +
                'Failure Rate: %{y:.1%}<br>' +
                'Avg Execution Time: %{x:.2f}ms<br>' +
                'Error Count: %{marker.color}<extra></extra>'
            )
        else:
            x_data = failures['count']
            x_title = 'Error Count'
            hover_template = (
                '<b>%{text}</b><br>' +
                'Failure Rate: %{y:.1%}<br>' +
                'Error Count: %{x}<br>' +
                'Total Errors: %{marker.color}<extra></extra>'
            )

        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=failures['failure_rate'],
                mode='markers+text',
                marker=dict(
                    size=failures['count']*10,
                    color=failures['count'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Error Count", x=1.15)
                ),
                text=failures['tool_name'],
                textposition='top center',
                name='Tools',
                hovertemplate=hover_template
            ),
            row=1, col=2
        )

        # 3. Error types distribution (bottom-left)
        error_types = failures.groupby('error_category')['count'].sum()
        fig.add_trace(
            go.Bar(
                x=error_types.index,
                y=error_types.values,
                name='Error Count',
                marker_color='orange',
                text=[f"{count}<br>({count/error_types.sum():.1%})" for count in error_types.values],
                textposition='outside'
            ),
            row=2, col=1
        )

        # 4. Failure details table (bottom-right)
        table_data = failures.head(10)  # Top 10 failures

        # Determine table columns based on available data
        if 'avg_execution_time' in failures.columns:
            headers = ['<b>Tool</b>', '<b>Error Type</b>', '<b>Count</b>', '<b>Failure Rate</b>', '<b>Avg Time (ms)</b>']
            cell_values = [
                table_data['tool_name'],
                table_data['error_category'],
                table_data['count'],
                [f"{rate:.1%}" for rate in table_data['failure_rate']],
                [f"{time*1000:.2f}ms" for time in table_data['avg_execution_time']]
            ]
        else:
            headers = ['<b>Tool</b>', '<b>Error Type</b>', '<b>Count</b>', '<b>Failure Rate</b>', '<b>Simulations</b>']
            cell_values = [
                table_data['tool_name'],
                table_data['error_category'],
                table_data['count'],
                [f"{rate:.1%}" for rate in table_data['failure_rate']],
                table_data.get('simulations_affected', ['N/A'] * len(table_data))
            ]

        fig.add_trace(
            go.Table(
                header=dict(
                    values=headers,
                    fill_color='lightcoral',
                    align='center',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=cell_values,
                    fill_color=[['white', 'lightgray']*len(table_data)],
                    align='center',
                    font=dict(size=11)
                )
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            title_text="🔍 Comprehensive Failure Analysis Dashboard",
            showlegend=False,
            height=800
        )

        # Update axes
        fig.update_xaxes(title_text="Failure Count", row=1, col=1)
        fig.update_yaxes(title_text="Tools", row=1, col=1)
        fig.update_xaxes(title_text=x_title, row=1, col=2)
        fig.update_yaxes(title_text="Failure Rate", row=1, col=2, tickformat='.0%')
        fig.update_xaxes(title_text="Error Category", row=2, col=1)
        fig.update_yaxes(title_text="Error Count", row=2, col=1)

        return fig

    def create_state_change_plot(self) -> go.Figure:
        """
        Creates a comprehensive plot comparing performance of state-changing vs.
        read-only tool calls with detailed breakdown by function names.

        Returns:
            A Plotly Figure object with subplots showing both overview and detailed breakdown.
        """
        state_analysis_df = self.analyzer.get_state_change_analysis()
        if state_analysis_df.empty:
            return go.Figure().update_layout(
                title="No State Change Data Available"
            )

        # Create subplots: overview and detailed breakdown
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "bar", "colspan": 2}, None],
                [{"type": "bar"}, {"type": "bar"}]
            ],
            subplot_titles=(
                "State Change Analysis by Tool",
                "State-Changing Tools Performance",
                "Read-Only Tools Performance"
            ),
            row_heights=[0.5, 0.5]
        )

        # Main plot: All tools grouped by state change type
        fig.add_trace(
            go.Bar(
                name="State-Changing",
                x=state_analysis_df[state_analysis_df['state_changed'] == True]['tool_name'],
                y=state_analysis_df[state_analysis_df['state_changed'] == True]['total_calls'],
                marker_color=state_analysis_df[state_analysis_df['state_changed'] == True]['success_rate'],
                marker_colorscale='RdYlGn',
                marker_cmin=0,
                marker_cmax=1,
                text=state_analysis_df[state_analysis_df['state_changed'] == True]['total_calls'],
                textposition='outside',
                hovertemplate=(
                    '<b>%{x}</b><br>' +
                    'Calls: %{y}<br>' +
                    'Success Rate: %{marker.color:.2%}<br>' +
                    'Type: State-Changing<extra></extra>'
                ),
                showlegend=True
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(
                name="Read-Only",
                x=state_analysis_df[state_analysis_df['state_changed'] == False]['tool_name'],
                y=state_analysis_df[state_analysis_df['state_changed'] == False]['total_calls'],
                marker_color=state_analysis_df[state_analysis_df['state_changed'] == False]['success_rate'],
                marker_colorscale='RdYlGn',
                marker_cmin=0,
                marker_cmax=1,
                text=state_analysis_df[state_analysis_df['state_changed'] == False]['total_calls'],
                textposition='outside',
                hovertemplate=(
                    '<b>%{x}</b><br>' +
                    'Calls: %{y}<br>' +
                    'Success Rate: %{marker.color:.2%}<br>' +
                    'Type: Read-Only<extra></extra>'
                ),
                showlegend=True
            ),
            row=1, col=1
        )

        # State-changing tools detailed view
        state_changing = state_analysis_df[state_analysis_df['state_changed'] == True]
        if not state_changing.empty:
            fig.add_trace(
                go.Bar(
                    x=state_changing['tool_name'],
                    y=state_changing['success_rate'],
                    name="Success Rate",
                    marker_color='lightgreen',
                    text=[f"{rate:.1%}" for rate in state_changing['success_rate']],
                    textposition='outside',
                    showlegend=False
                ),
                row=2, col=1
            )

        # Read-only tools detailed view
        read_only = state_analysis_df[state_analysis_df['state_changed'] == False]
        if not read_only.empty:
            fig.add_trace(
                go.Bar(
                    x=read_only['tool_name'],
                    y=read_only['success_rate'],
                    name="Success Rate",
                    marker_color='lightblue',
                    text=[f"{rate:.1%}" for rate in read_only['success_rate']],
                    textposition='outside',
                    showlegend=False
                ),
                row=2, col=2
            )

        # Update layout
        fig.update_layout(
            title_text="State Change Analysis: Tool Performance Breakdown",
            showlegend=True,
            height=800
        )

        # Update axes labels
        fig.update_xaxes(title_text="Tools", row=1, col=1)
        fig.update_yaxes(title_text="Total Calls", row=1, col=1)
        fig.update_xaxes(title_text="State-Changing Tools", row=2, col=1)
        fig.update_yaxes(title_text="Success Rate", row=2, col=1, range=[0, 1.1])
        fig.update_xaxes(title_text="Read-Only Tools", row=2, col=2)
        fig.update_yaxes(title_text="Success Rate", row=2, col=2, range=[0, 1.1])

        return fig

    def create_tool_flow_sankey(self) -> go.Figure:
        """
        Creates a Sankey diagram to visualize the flow between tool calls.

        Returns:
            A Plotly Figure object representing the tool flow.
        """
        sequence_df = self.analyzer.get_tool_sequence_analysis()
        if sequence_df.empty:
            return go.Figure().update_layout(title="Not enough data for a flow diagram")

        # Create a list of unique tool names (nodes)
        all_nodes = pd.concat([sequence_df['source'], sequence_df['target']]).unique()
        node_map = {node: i for i, node in enumerate(all_nodes)}

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes,
            ),
            link=dict(
                source=[node_map[s] for s in sequence_df['source']],
                target=[node_map[t] for t in sequence_df['target']],
                value=sequence_df['count']
            ))])

        fig.update_layout(title_text="Tool Call Flow Analysis", font_size=10)
        return fig

    def create_performance_bottleneck_plot(self) -> go.Figure:
        """
        Create a plot to identify performance bottlenecks.

        Returns:
            A Plotly Figure object.
        """
        tool_perf = self.analyzer.get_tool_performance()
        if tool_perf.empty:
            return go.Figure().update_layout(title="No Performance Data")

        fig = px.scatter(
            tool_perf,
            x='total_calls',
            y='avg_execution_time',
            size='total_execution_time',
            color='tool_name',
            hover_name='tool_name',
            text='tool_name',
            size_max=60,
            title="Performance Bottlenecks: Calls vs. Avg. Time"
        )
        fig.update_traces(textposition='middle center', textfont_size=8)
        fig.update_layout(
            xaxis_title="Total Calls",
            yaxis_title="Average Execution Time (ms)"
        )
        return fig

    def create_tool_report(self, output_path: str, log_file_name: str = "execution_logs") -> str:
        """
        Create a comprehensive HTML report with detailed analysis, insights, and embedded plots.

        Args:
            output_path: Path where the report HTML will be saved
            log_file_name: Name of the original log file for reference

        Returns:
            Path to the created report HTML file
        """
        from datetime import datetime
        import base64
        from io import BytesIO

        # Get all analysis data
        summary = self.analyzer.get_summary_metrics()
        tool_perf = self.analyzer.get_tool_performance()
        failures = self.analyzer.get_failure_analysis()
        state_analysis = self.analyzer.get_state_change_analysis()
        sequence_analysis = self.analyzer.get_tool_sequence_analysis()

        # Generate all plots
        summary_fig = self.create_summary_dashboard(include_task_success=False)  # Don't duplicate task success in tool report
        failure_fig = self.create_failure_analysis_plot()
        state_fig = self.create_state_change_plot()
        sankey_fig = self.create_tool_flow_sankey()
        bottleneck_fig = self.create_performance_bottleneck_plot()

        # Convert plots to embedded HTML
        summary_html = summary_fig.to_html(include_plotlyjs='inline', div_id="summary-plot")
        failure_html = failure_fig.to_html(include_plotlyjs=False, div_id="failure-plot")
        state_html = state_fig.to_html(include_plotlyjs=False, div_id="state-plot")
        sankey_html = sankey_fig.to_html(include_plotlyjs=False, div_id="sankey-plot")
        bottleneck_html = bottleneck_fig.to_html(include_plotlyjs=False, div_id="bottleneck-plot")

        # Generate insights
        insights = self._generate_key_insights(summary, tool_perf, failures, state_analysis, sequence_analysis)
        recommendations = self._generate_recommendations(summary, tool_perf, failures, state_analysis)

        # Create comprehensive HTML report
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tool Execution Analysis Report</title>
    <style>
        @media print {{
            .no-print {{ display: none; }}
            .page-break {{ page-break-before: always; }}
            body {{ font-size: 12px; }}
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}

        .header {{
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}

        .header .subtitle {{
            color: #6c757d;
            font-size: 1.1em;
            margin: 10px 0;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section h2 {{
            color: #2c3e50;
            border-left: 4px solid #007bff;
            padding-left: 15px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .section h3 {{
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.3em;
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
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .metric-value {{
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .insight-box {{
            background: #e8f4fd;
            border-left: 4px solid #007bff;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .insight-box h4 {{
            color: #007bff;
            margin-top: 0;
        }}

        .recommendation-box {{
            background: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .recommendation-box h4 {{
            color: #28a745;
            margin-top: 0;
        }}

        .warning-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .warning-box h4 {{
            color: #856404;
            margin-top: 0;
        }}

        .table-container {{
            overflow-x: auto;
            margin: 20px 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}

        th {{
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        .plot-container {{
            margin: 30px 0;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            overflow: hidden;
        }}

        .status-excellent {{ color: #28a745; font-weight: bold; }}
        .status-good {{ color: #17a2b8; font-weight: bold; }}
        .status-fair {{ color: #ffc107; font-weight: bold; }}
        .status-poor {{ color: #dc3545; font-weight: bold; }}

        /* Enhanced Failure Analysis Styles */
        .failure-section {{
            background: #fff;
            border-radius: 8px;
            padding: 20px;
        }}

        .success-section {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .failure-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}

        .stat-card h4 {{
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #dc3545;
        }}

        .failure-modes {{
            margin-bottom: 30px;
        }}

        .failure-mode {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .performance-impact {{
            margin-bottom: 30px;
        }}

        .poor-performers, .slowest-tools {{
            margin-bottom: 20px;
        }}

        .performance-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}

        .performance-table th {{
            background-color: #dc3545;
            color: white;
        }}

        .failure-insights {{
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .failure-insights ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}

        .failure-insights li {{
            margin-bottom: 8px;
        }}

        .recommendations {{
            background: #f3e5f5;
            border: 1px solid #e1bee7;
            border-radius: 8px;
            padding: 20px;
        }}

        .recommendations ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}

        .recommendations li {{
            margin-bottom: 10px;
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🔍 Tool Execution Analysis Report</h1>
            <div class="subtitle">
                Comprehensive analysis of tool performance and execution patterns<br>
                Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}<br>
                Source: {log_file_name}
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="section">
            <h2>📊 Executive Summary</h2>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{summary.get('total_simulations', 'N/A')}</div>
                    <div class="metric-label">Total Simulations</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('total_tool_calls', 0)}</div>
                    <div class="metric-label">Total Tool Calls</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('average_execution_time', 0)*1000:.2f}ms</div>
                    <div class="metric-label">Avg Execution Time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('tools_used', 0)}</div>
                    <div class="metric-label">Unique Tools</div>
                </div>
            </div>

            <div class="plot-container">
                {summary_html}
            </div>
        </div>

        <!-- Key Insights -->
        <div class="section">
            <h2>💡 Key Insights</h2>
            {insights}
        </div>

        <!-- Tool Performance Analysis -->
        <div class="section page-break">
            <h2>🛠️ Tool Performance Analysis</h2>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Tool Name</th>
                            <th>Total Calls</th>
                            <th>Success Rate</th>
                            <th>Avg Time (ms)</th>
                            <th>Performance</th>
                            <th>State Changes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_tool_performance_table(tool_perf)}
                    </tbody>
                </table>
            </div>

            <div class="plot-container">
                {bottleneck_html}
            </div>
        </div>

        <!-- State Change Analysis -->
        <div class="section page-break">
            <h2>🔄 State Change Analysis</h2>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Tool Name</th>
                            <th>Category</th>
                            <th>Calls</th>
                            <th>Success Rate</th>
                            <th>Avg Time (ms)</th>
                            <th>Performance Rating</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_state_analysis_table(state_analysis)}
                    </tbody>
                </table>
            </div>

            <div class="plot-container">
                {state_html}
            </div>
        </div>

        <!-- Failure Analysis -->
        <div class="section page-break">
            <h2>🔥 Failure Analysis</h2>

            {self._generate_enhanced_failure_section(failures, summary, tool_perf)}

            <div class="plot-container">
                {failure_html}
            </div>
        </div>

        <!-- Tool Flow Analysis -->
        <div class="section page-break">
            <h2>🔗 Tool Flow Analysis</h2>

            <div class="insight-box">
                <h4>Tool Sequence Patterns</h4>
                {self._generate_sequence_insights(sequence_analysis)}
            </div>

            <div class="plot-container">
                {sankey_html}
            </div>
        </div>

        <!-- Recommendations -->
        <div class="section page-break">
            <h2>📋 Recommendations</h2>
            {recommendations}
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Report generated by tau2-enhanced analysis framework</p>
            <p>For questions or support, refer to the project documentation</p>
        </div>
    </div>
</body>
</html>
"""

        # Write the report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _generate_key_insights(self, summary, tool_perf, failures, state_analysis, sequence_analysis):
        """Generate key insights from the analysis data."""
        insights_html = ""

        # Performance insights
        if not tool_perf.empty:
            excellent_tools = len(tool_perf[tool_perf['performance_category'] == 'excellent'])
            poor_tools = len(tool_perf[tool_perf['performance_category'] == 'poor'])
            most_used = tool_perf.iloc[0]['tool_name'] if len(tool_perf) > 0 else "N/A"

            insights_html += f"""
            <div class="insight-box">
                <h4>🎯 Performance Insights</h4>
                <ul>
                    <li><strong>{excellent_tools}</strong> out of {len(tool_perf)} tools have excellent performance (≥95% success rate)</li>
                    <li><strong>{most_used}</strong> is the most frequently used tool with {tool_perf.iloc[0]['total_calls']} calls</li>
                    <li>Overall system reliability: <strong>{summary.get('tool_success_rate', 0):.1%}</strong></li>
                </ul>
            </div>
            """

        # State change insights
        if not state_analysis.empty:
            state_changing = state_analysis[state_analysis['state_changed'] == True]
            read_only = state_analysis[state_analysis['state_changed'] == False]

            insights_html += f"""
            <div class="insight-box">
                <h4>🔄 State Management Insights</h4>
                <ul>
                    <li><strong>{len(state_changing)}</strong> tools perform state changes, <strong>{len(read_only)}</strong> are read-only</li>
                    <li>State-changing operations: {state_changing['total_calls'].sum() if not state_changing.empty else 0} calls</li>
                    <li>Read-only operations: {read_only['total_calls'].sum() if not read_only.empty else 0} calls</li>
                </ul>
            </div>
            """

        # Failure insights
        if not failures.empty:
            total_errors = failures['count'].sum()
            error_types = failures['error_category'].nunique()

            insights_html += f"""
            <div class="warning-box">
                <h4>⚠️ Error Analysis</h4>
                <ul>
                    <li><strong>{total_errors}</strong> total errors across <strong>{error_types}</strong> error types</li>
                    <li>Most problematic tool: <strong>{failures.iloc[0]['tool_name']}</strong> ({failures.iloc[0]['count']} errors)</li>
                    <li>Primary error type: <strong>{failures.iloc[0]['error_category']}</strong></li>
                </ul>
            </div>
            """
        else:
            insights_html += f"""
            <div class="insight-box">
                <h4>✅ Error Analysis</h4>
                <p><strong>Excellent!</strong> No errors detected in the execution logs. All tools are performing reliably.</p>
            </div>
            """

        return insights_html

    def _generate_recommendations(self, summary, tool_perf, failures, state_analysis):
        """Generate data-driven actionable recommendations based on actual analysis results."""
        recommendations_html = ""

        # Analyze the data to generate specific recommendations
        recommendations = self._analyze_and_generate_recommendations(summary, tool_perf, failures, state_analysis)

        # Group recommendations by priority and type
        high_priority = recommendations.get('high_priority', [])
        medium_priority = recommendations.get('medium_priority', [])
        low_priority = recommendations.get('low_priority', [])

        # High Priority Recommendations (Critical Issues)
        if high_priority:
            recommendations_html += f"""
            <div class="recommendation-box" style="border-left: 4px solid #dc3545;">
                <h4>🚨 High Priority Actions</h4>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in high_priority])}
                </ul>
            </div>
            """

        # Medium Priority Recommendations (Performance Improvements)
        if medium_priority:
            recommendations_html += f"""
            <div class="recommendation-box" style="border-left: 4px solid #ffc107;">
                <h4>⚡ Performance Optimizations</h4>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in medium_priority])}
                </ul>
            </div>
            """

        # Low Priority Recommendations (Best Practices)
        if low_priority:
            recommendations_html += f"""
            <div class="recommendation-box">
                <h4>📈 Enhancement Opportunities</h4>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in low_priority])}
                </ul>
            </div>
            """

        # If no specific recommendations, provide positive feedback
        if not any([high_priority, medium_priority, low_priority]):
            recommendations_html += f"""
            <div class="insight-box">
                <h4>✅ System Performance Excellent</h4>
                <p><strong>Outstanding!</strong> Your system is performing exceptionally well with no critical issues identified.</p>
                <p>Continue monitoring and maintain current operational standards.</p>
            </div>
            """

        return recommendations_html

    def _analyze_and_generate_recommendations(self, summary, tool_perf, failures, state_analysis):
        """Analyze data and generate specific, actionable recommendations."""
        high_priority = []
        medium_priority = []
        low_priority = []

        # Analyze overall system health
        success_rate = summary.get('tool_success_rate', 1.0)
        total_calls = summary.get('total_tool_calls', 0)
        avg_execution_time = summary.get('average_execution_time', 0)

        # High Priority: Critical reliability issues
        if success_rate < 0.8:
            high_priority.append(f"<strong>Critical:</strong> System success rate is only {success_rate:.1%}. Immediate investigation required.")

        if not failures.empty:
            # Analyze specific failure patterns
            total_failures = failures['count'].sum()
            failure_rate = total_failures / total_calls if total_calls > 0 else 0

            if failure_rate > 0.1:  # More than 10% failure rate
                high_priority.append(f"<strong>High failure rate:</strong> {failure_rate:.1%} of calls are failing across the system.")

            # Specific error type recommendations
            error_types = failures['error_category'].unique()
            for error_type in error_types:
                error_count = failures[failures['error_category'] == error_type]['count'].sum()
                affected_tools = failures[failures['error_category'] == error_type]['tool_name'].unique()

                if error_type == 'ValidationError':
                    high_priority.append(f"<strong>Input validation critical:</strong> {error_count} ValidationErrors across {len(affected_tools)} tools: {', '.join(affected_tools[:3])}")
                elif error_type == 'TimeoutError':
                    high_priority.append(f"<strong>Timeout issues:</strong> {error_count} timeouts detected across {len(affected_tools)} tools.")
                elif error_type == 'ConnectionError':
                    high_priority.append(f"<strong>Connection failures:</strong> {error_count} connection errors affecting {len(affected_tools)} tools.")

        # Analyze tool performance for medium priority recommendations
        if not tool_perf.empty:
            # Poor performing tools
            poor_tools = tool_perf[tool_perf['performance_category'] == 'poor']
            if not poor_tools.empty:
                poor_list = poor_tools['tool_name'].tolist()
                failure_rates = poor_tools['error_rate'].tolist()
                medium_priority.append(f"<strong>Poor performing tools:</strong> {len(poor_list)} tools identified: " +
                                     ", ".join([f"{tool} ({rate:.1%} failure)" for tool, rate in zip(poor_list[:3], failure_rates[:3])]))

            # Slow tools
            slow_threshold = max(0.1, avg_execution_time * 5)  # Dynamic threshold
            slow_tools = tool_perf[tool_perf['avg_execution_time'] > slow_threshold]
            if not slow_tools.empty:
                slow_list = slow_tools['tool_name'].tolist()
                slow_times = slow_tools['avg_execution_time'].tolist()
                medium_priority.append(f"<strong>Performance optimization needed:</strong> " +
                                     ", ".join([f"{tool} ({time:.3f}s avg)" for tool, time in zip(slow_list[:3], slow_times[:3])]))

            # High-volume tools identification (data observation only)
            high_volume = tool_perf[tool_perf['total_calls'] > tool_perf['total_calls'].quantile(0.8)]
            if not high_volume.empty and len(high_volume) > 0:
                cache_candidates = high_volume['tool_name'].tolist()[:3]
                medium_priority.append(f"<strong>High usage pattern:</strong> Top usage tools account for {len(high_volume)} of {len(tool_perf)} total tools: {', '.join(cache_candidates)}")

        # State change analysis recommendations
        if not state_analysis.empty:
            state_changing = state_analysis[state_analysis['state_changed'] == True]
            read_only = state_analysis[state_analysis['state_changed'] == False]

            # Check if state-changing operations have different error patterns than read-only
            if not state_changing.empty and not read_only.empty:
                state_error_rate = state_changing['error_rate'].mean()
                readonly_error_rate = read_only['error_rate'].mean()

                if state_error_rate > readonly_error_rate * 2:  # State operations much more error-prone
                    medium_priority.append(f"<strong>State operation pattern:</strong> State-changing operations have {state_error_rate:.1%} error rate vs {readonly_error_rate:.1%} for read-only operations.")

        # Data pattern observations (no hardcoded recommendations)
        if not tool_perf.empty:
            most_used = tool_perf.iloc[0]
            usage_ratio = most_used['total_calls'] / total_calls
            if usage_ratio > 0.5:  # One tool dominates usage - just report the pattern
                low_priority.append(f"<strong>Usage concentration:</strong> {most_used['tool_name']} accounts for {usage_ratio:.1%} of all calls.")

        if success_rate > 0.95:  # Report excellent performance
            low_priority.append(f"<strong>System performance:</strong> Excellent {success_rate:.1%} success rate achieved across {total_calls} calls.")

        if len(tool_perf) > 5:  # Report system complexity
            low_priority.append(f"<strong>System scope:</strong> Analysis covers {len(tool_perf)} different tools across {total_calls} total calls.")

        return {
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority
        }

    def _generate_tool_performance_table(self, tool_perf):
        """Generate HTML table rows for tool performance."""
        if tool_perf.empty:
            return "<tr><td colspan='6'>No performance data available</td></tr>"

        rows = []
        for _, row in tool_perf.iterrows():
            status_class = f"status-{row['performance_category']}"
            state_changes = f"{int(row['state_changing_calls'])}/{int(row['total_calls'])}"

            rows.append(f"""
            <tr>
                <td><strong>{row['tool_name']}</strong></td>
                <td>{int(row['total_calls'])}</td>
                <td>{row['success_rate']:.1%}</td>
                <td>{row['avg_execution_time']*1000:.2f}ms</td>
                <td class="{status_class}">{row['performance_category'].title()}</td>
                <td>{state_changes}</td>
            </tr>
            """)

        return "".join(rows)

    def _generate_state_analysis_table(self, state_analysis):
        """Generate HTML table rows for state analysis."""
        if state_analysis.empty:
            return "<tr><td colspan='6'>No state change data available</td></tr>"

        rows = []
        for _, row in state_analysis.iterrows():
            status_class = f"status-{row['performance_rating']}"

            rows.append(f"""
            <tr>
                <td><strong>{row['tool_name']}</strong></td>
                <td>{row['category']}</td>
                <td>{int(row['total_calls'])}</td>
                <td>{row['success_rate']:.1%}</td>
                <td>{row['avg_execution_time']*1000:.2f}ms</td>
                <td class="{status_class}">{row['performance_rating'].title()}</td>
            </tr>
            """)

        return "".join(rows)

    def _generate_failure_section(self, failures, summary):
        """Generate the failure analysis section content."""
        if failures.empty:
            return """
            <div class="insight-box">
                <h4>✅ System Reliability</h4>
                <p><strong>Outstanding performance!</strong> No failures detected during execution.</p>
                <p>All tool calls completed successfully, demonstrating excellent system stability.</p>
            </div>
            """

        total_errors = failures['count'].sum()
        error_rate = total_errors / summary.get('total_tool_calls', 1)

        failure_html = f"""
        <div class="warning-box">
            <h4>📊 Failure Statistics</h4>
            <ul>
                <li>Total failures: <strong>{total_errors}</strong></li>
                <li>Overall error rate: <strong>{error_rate:.1%}</strong></li>
                <li>Affected tools: <strong>{failures['tool_name'].nunique()}</strong></li>
                <li>Error categories: <strong>{failures['error_category'].nunique()}</strong></li>
            </ul>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Tool Name</th>
                        <th>Error Type</th>
                        <th>Count</th>
                        <th>Failure Rate</th>"""

        # Determine which additional columns are available
        if 'avg_execution_time' in failures.columns:
            failure_html += """
                        <th>Avg Time (ms)</th>"""
        if 'simulations_affected' in failures.columns:
            failure_html += """
                        <th>Simulations</th>"""
        if 'first_occurrence' in failures.columns:
            failure_html += """
                        <th>First Occurrence</th>"""

        failure_html += """
                    </tr>
                </thead>
                <tbody>
        """

        for _, row in failures.head(10).iterrows():
            failure_html += f"""
            <tr>
                <td><strong>{row['tool_name']}</strong></td>
                <td>{row['error_category']}</td>
                <td>{int(row['count'])}</td>
                <td>{row['failure_rate']:.1%}</td>"""

            # Add available columns dynamically
            if 'avg_execution_time' in failures.columns:
                failure_html += f"""
                <td>{row['avg_execution_time']*1000:.2f}ms</td>"""
            if 'simulations_affected' in failures.columns:
                failure_html += f"""
                <td>{row['simulations_affected']}</td>"""
            if 'first_occurrence' in failures.columns:
                failure_html += f"""
                <td>{str(row['first_occurrence'])[:19]}</td>"""

            failure_html += """
            </tr>
            """

        failure_html += """
                </tbody>
            </table>
        </div>
        """

        return failure_html

    def _generate_sequence_insights(self, sequence_analysis):
        """Generate insights about tool sequence patterns."""
        if sequence_analysis.empty:
            return "<p>No sequence patterns detected in the execution flow.</p>"

        insights = "<p>Most common tool transitions:</p><ul>"

        for _, row in sequence_analysis.head(5).iterrows():
            insights += f"<li><strong>{row['source']}</strong> → <strong>{row['target']}</strong> ({int(row['count'])} times)</li>"

        insights += "</ul>"

        # Add pattern analysis
        self_loops = sequence_analysis[sequence_analysis['source'] == sequence_analysis['target']]
        if not self_loops.empty:
            insights += f"<p><strong>Recursive patterns:</strong> {len(self_loops)} tools frequently call themselves, indicating iterative processing patterns.</p>"

        return insights

    def create_comprehensive_report(self, output_path: str, log_file_name: str = "execution_logs") -> str:
        """
        Create a comprehensive HTML report with simulation overviews, transcripts, and results.
        """
        from datetime import datetime

        summary = self.analyzer.get_summary_metrics()
        simulations = self.analyzer.raw_log_data.get('simulations', [])
        tasks = {task['id']: task for task in self.analyzer.raw_log_data.get('tasks', [])}

        def format_message(msg):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            tool_calls = msg.get('tool_calls')
            
            color = {
                'assistant': '#2b5797',
                'user': '#008a00',
                'tool': '#6a00ff'
            }.get(role, '#333')

            html = f'<div class="message" style="border-left-color: {color};">'
            html += f'<div class="role" style="color: {color};">{role.title()}</div>'
            if content:
                html += f'<div class="content">{content.replace(">", "&gt;").replace("<", "&lt;")}</div>'
            if tool_calls:
                html += '<div class="tool-calls">'
                for tc in tool_calls:
                    html += f'<div class="tool-call"><strong>Tool:</strong> {tc.get("name", "N/A")}'
                    html += f'<pre>{json.dumps(tc.get("arguments", {}), indent=2)}</pre></div>'
                html += '</div>'
            html += '</div>'
            return html

        sim_html = ""
        for sim in simulations:
            task_id = sim.get('task_id')
            task = tasks.get(task_id, {})
            reward_info = sim.get('reward_info', {})
            reward = reward_info.get('reward', 0)
            status = "✅ Success" if reward > 0 else "❌ Failure"
            
            sim_html += f'<div class="simulation">'
            sim_html += f'<h3>Task: {task_id} ({status})</h3>'
            sim_html += f'<p><strong>Description:</strong> {task.get("description", {}).get("purpose", "N/A")}</p>'
            sim_html += f'<p><strong>Termination Reason:</strong> {sim.get("termination_reason", "N/A")}</p>'
            sim_html += f'<p><strong>Final Reward:</strong> {reward:.2f}</p>'
            
            sim_html += '<h4>Conversation Transcript:</h4>'
            sim_html += '<div class="transcript">'
            for msg in sim.get('messages', []):
                sim_html += format_message(msg)
            sim_html += '</div></div>'

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Comprehensive Simulation Report</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                .container {{ max-width: 1000px; margin: auto; }}
                .simulation {{ border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin-bottom: 20px; }}
                .message {{ border-left: 4px solid; padding: 10px; margin-bottom: 10px; background-color: #f9f9f9; }}
                .role {{ font-weight: bold; margin-bottom: 5px; }}
                .tool-call {{ background-color: #eee; padding: 5px; border-radius: 3px; }}
                pre {{ white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Comprehensive Simulation Report</h1>
                <p><strong>Source:</strong> {log_file_name}</p>
                <p><strong>Task Success Rate:</strong> {summary.get('task_success_rate', 0):.1%}</p>
                {sim_html}
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def create_markdown_report(self, output_path: str, log_file_name: str = "execution_logs") -> str:
        """
        Create a comprehensive markdown report with detailed analysis and insights.

        Args:
            output_path: Path where the markdown report will be saved
            log_file_name: Name of the original log file for reference

        Returns:
            Path to the created markdown report file
        """
        from datetime import datetime

        # Get all analysis data
        summary = self.analyzer.get_summary_metrics()
        tool_perf = self.analyzer.get_tool_performance()
        failures = self.analyzer.get_failure_analysis()
        state_analysis = self.analyzer.get_state_change_analysis()
        sequence_analysis = self.analyzer.get_tool_sequence_analysis()

        # Generate insights and recommendations (markdown format)
        insights = self._generate_key_insights_md(summary, tool_perf, failures, state_analysis, sequence_analysis)
        recommendations = self._generate_recommendations_md(summary, tool_perf, failures, state_analysis)

        # Start building the markdown content
        md_content = f"""# Enhanced Tau2 Execution Analysis Report

**Source File:** `{log_file_name}`
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Framework:** Enhanced Tau2 Logging & Analytics

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Simulations** | {summary.get('total_simulations', 'N/A')} |
| **Successful Simulations** | {summary.get('successful_simulations', 'N/A')} |
| **Task Success Rate** | {summary.get('task_success_rate', 0):.1%} |
| **Total Tool Calls** | {summary.get('total_tool_calls', 0)} |
| **Tool Success Rate** | {summary.get('tool_success_rate', 0):.1%} |
| **Tool Error Rate** | {summary.get('tool_error_rate', 0):.1%} |
| **State Changing Calls** | {summary.get('state_changing_calls', 0)} |
| **Average Execution Time** | {summary.get('average_execution_time', 0)*1000:.2f}ms |
| **Success Metric Source** | {summary.get('success_metric_source', 'N/A')} |

---

## 🛠️ Tool Performance Analysis

"""

        if not tool_perf.empty:
            md_content += "### Performance Overview\n\n"
            md_content += "| Tool Name | Calls | Success Rate | Avg Time (ms) | Category |\n"
            md_content += "|-----------|-------|--------------|---------------|----------|\n"

            for _, row in tool_perf.head(10).iterrows():
                md_content += f"| {row['tool_name']} | {int(row['total_calls'])} | {row['success_rate']:.1%} | {row['avg_execution_time']*1000:.2f} | {row['performance_category'].title()} |\n"

            # Performance categories breakdown
            perf_categories = tool_perf['performance_category'].value_counts()
            md_content += "\n### Performance Distribution\n\n"
            for category, count in perf_categories.items():
                md_content += f"- **{category.title()}**: {count} tools\n"

        else:
            md_content += "No tool performance data available.\n"

        md_content += "\n---\n\n## 🔥 Failure Analysis\n\n"

        if not failures.empty:
            md_content += "### Failure Overview\n\n"
            md_content += "| Tool Name | Error Type | Count | Failure Rate |\n"
            md_content += "|-----------|------------|-------|-------------|\n"

            for _, row in failures.head(10).iterrows():
                md_content += f"| {row['tool_name']} | {row['error_category']} | {int(row['count'])} | {row['failure_rate']:.1%} |\n"

            # Failure insights
            total_failures = failures['count'].sum()
            affected_tools = failures['tool_name'].nunique()
            md_content += f"\n**Key Failure Metrics:**\n"
            md_content += f"- Total failures: **{total_failures}**\n"
            md_content += f"- Affected tools: **{affected_tools}**\n"
            md_content += f"- Error categories: **{failures['error_category'].nunique()}**\n"

            # Most problematic error types
            error_types = failures.groupby('error_category')['count'].sum().sort_values(ascending=False)
            md_content += f"\n**Most Common Error Types:**\n"
            for error_type, count in error_types.head(5).items():
                md_content += f"- {error_type}: {count} occurrences\n"

        else:
            md_content += "🎉 **No failures detected!** All tool calls completed successfully.\n"

        md_content += "\n---\n\n## 🔄 State Change Analysis\n\n"

        if not state_analysis.empty:
            state_changing = state_analysis[state_analysis['state_changed'] == True]
            read_only = state_analysis[state_analysis['state_changed'] == False]

            md_content += f"### State-Changing Tools ({len(state_changing)} tools)\n\n"
            if not state_changing.empty:
                md_content += "| Tool Name | Calls | Success Rate | Avg Time (ms) |\n"
                md_content += "|-----------|-------|--------------|---------------|\n"
                for _, row in state_changing.iterrows():
                    md_content += f"| {row['tool_name']} | {int(row['total_calls'])} | {row['success_rate']:.1%} | {row['avg_execution_time']*1000:.2f} |\n"
            else:
                md_content += "No state-changing tools found.\n"

            md_content += f"\n### Read-Only Tools ({len(read_only)} tools)\n\n"
            if not read_only.empty:
                md_content += "| Tool Name | Calls | Success Rate | Avg Time (ms) |\n"
                md_content += "|-----------|-------|--------------|---------------|\n"
                for _, row in read_only.head(10).iterrows():
                    md_content += f"| {row['tool_name']} | {int(row['total_calls'])} | {row['success_rate']:.1%} | {row['avg_execution_time']*1000:.2f} |\n"
            else:
                md_content += "No read-only tools found.\n"

        else:
            md_content += "No state change data available.\n"

        md_content += "\n---\n\n## 🔗 Tool Sequence Patterns\n\n"

        if not sequence_analysis.empty:
            md_content += "### Most Common Tool Transitions\n\n"
            md_content += "| From Tool | To Tool | Count |\n"
            md_content += "|-----------|---------|-------|\n"

            for _, row in sequence_analysis.head(10).iterrows():
                md_content += f"| {row['source']} | {row['target']} | {int(row['count'])} |\n"
        else:
            md_content += "No sequence pattern data available.\n"

        md_content += "\n---\n\n## 🔍 Key Insights\n\n"
        for insight in insights:
            md_content += f"- {insight}\n"

        md_content += "\n---\n\n## 💡 Recommendations\n\n"
        for recommendation in recommendations:
            md_content += f"- {recommendation}\n"

        # Add detailed failure analysis similar to non_enhanced script
        md_content += self._generate_detailed_failure_analysis_md(summary, failures, tool_perf)

        # Add advanced failure pattern analysis
        md_content += self._generate_advanced_failure_patterns_md(summary, failures, tool_perf)

        # Add task complexity and simulation analysis
        md_content += self._generate_task_simulation_analysis_md(summary, tool_perf, state_analysis)

        # Add communication vs tool call analysis
        md_content += self._generate_communication_analysis_md(summary, tool_perf, sequence_analysis)

        # Add performance issues deep dive
        md_content += self._generate_performance_deep_dive_md(tool_perf, sequence_analysis)

        # Add execution patterns and termination analysis
        md_content += self._generate_execution_patterns_md(summary, tool_perf, sequence_analysis)

        md_content += "\n---\n\n## 📈 Visualization Files\n\n"
        md_content += "The following interactive visualizations have been generated:\n\n"
        md_content += "- `summary_dashboard.html` - Executive dashboard with key metrics\n"
        md_content += "- `failure_analysis.html` - Detailed failure analysis charts\n"
        md_content += "- `state_change_analysis.html` - State change patterns and performance\n"
        md_content += "- `tool_flow_sankey.html` - Tool usage flow diagram\n"
        md_content += "- `performance_bottlenecks.html` - Performance analysis scatter plot\n"
        md_content += "- `tool_report.html` - Comprehensive HTML tool analysis report\n"
        md_content += "- `report.html` - Comprehensive HTML simulation report\n"

        md_content += f"\n---\n\n*Report generated by Enhanced Tau2 Analytics Framework*\n"

        # Write the markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return output_path

    def _generate_detailed_failure_analysis_md(self, summary, failures, tool_perf) -> str:
        """Generate detailed failure analysis section in markdown format."""
        md_content = "\n---\n\n## 🎯 Detailed Failure Analysis\n\n"

        if failures.empty:
            md_content += "### ✅ System Reliability\n\n"
            md_content += "**Outstanding performance!** No failures detected during execution.\n"
            md_content += "All tool calls completed successfully, demonstrating excellent system stability.\n"
            return md_content

        total_failures = failures['count'].sum()
        total_calls = summary.get('total_tool_calls', 1)
        error_rate = total_failures / total_calls

        md_content += f"### 📊 Failure Statistics\n\n"
        md_content += f"- **Total failures:** {total_failures}\n"
        md_content += f"- **Overall error rate:** {error_rate:.1%}\n"
        md_content += f"- **Affected tools:** {failures['tool_name'].nunique()}\n"
        md_content += f"- **Error categories:** {failures['error_category'].nunique()}\n"

        md_content += f"\n### 🚨 Root Cause Analysis\n\n"

        # Analyze failure patterns similar to the non_enhanced script
        if 'ActionCheckFailure' in failures['error_category'].values:
            action_failures = failures[failures['error_category'] == 'ActionCheckFailure']
            md_content += f"#### Action Check Failures\n\n"
            md_content += f"**{len(action_failures)} tools** failed action validation checks:\n\n"

            for _, row in action_failures.iterrows():
                md_content += f"- **{row['tool_name']}**: {int(row['count'])} failures "
                md_content += f"({row['failure_rate']:.1%} failure rate)\n"
                if 'simulations_affected' in failures.columns:
                    md_content += f"  - Affected {row['simulations_affected']} simulation(s)\n"
                if 'example_args' in failures.columns:
                    md_content += f"  - Example args: `{row['example_args']}`\n"

        # Performance impact analysis
        md_content += f"\n### ⚡ Performance Impact\n\n"

        # Find tools with both high usage and failures
        if not tool_perf.empty:
            high_usage_tools = tool_perf[tool_perf['total_calls'] >= 5]
            poor_performers = high_usage_tools[high_usage_tools['performance_category'] == 'poor']

            if not poor_performers.empty:
                md_content += f"**High-usage tools with poor performance:**\n\n"
                for _, row in poor_performers.iterrows():
                    md_content += f"- **{row['tool_name']}**: {int(row['total_calls'])} calls, "
                    md_content += f"{row['success_rate']:.1%} success rate\n"

            # Time-based analysis
            slowest_tools = tool_perf.nlargest(5, 'avg_execution_time')
            md_content += f"\n**Slowest tools by execution time:**\n\n"
            for _, row in slowest_tools.iterrows():
                md_content += f"- **{row['tool_name']}**: {row['avg_execution_time']*1000:.2f}ms average\n"

        md_content += f"\n### 💡 Failure Insights\n\n"

        # Generate insights based on failure patterns
        if not failures.empty:
            most_failed_tool = failures.loc[failures['count'].idxmax(), 'tool_name']
            most_failed_count = failures['count'].max()
            md_content += f"- **Most problematic tool:** {most_failed_tool} ({most_failed_count} failures)\n"

            if 'ActionCheckFailure' in failures['error_category'].values:
                md_content += f"- **Primary failure mode:** Action validation failures suggest issues with tool argument validation or execution logic\n"

            # Success vs failure comparison
            if not tool_perf.empty:
                avg_success_rate = tool_perf['success_rate'].mean()
                md_content += f"- **Average tool success rate:** {avg_success_rate:.1%}\n"

                if avg_success_rate < 0.8:
                    md_content += f"- **⚠️ Low overall success rate** suggests systemic issues requiring investigation\n"

        return md_content

    def _generate_enhanced_failure_section(self, failures, summary, tool_perf) -> str:
        """Generate enhanced failure analysis section for HTML reports, similar to non_enhanced script."""
        if failures.empty:
            return """
            <div class="success-section">
                <h3>✅ System Reliability</h3>
                <div class="insight-box">
                    <p><strong>Outstanding performance!</strong> No failures detected during execution.</p>
                    <p>All tool calls completed successfully, demonstrating excellent system stability.</p>
                </div>
            </div>
            """

        total_failures = failures['count'].sum()
        total_calls = summary.get('total_tool_calls', 1)
        error_rate = total_failures / total_calls
        affected_tools = failures['tool_name'].nunique()

        html = f"""
        <div class="failure-section">
            <h3>🎯 Root Cause Analysis</h3>
            <div class="failure-stats">
                <div class="stat-card">
                    <h4>Total Failures</h4>
                    <div class="stat-value">{total_failures}</div>
                </div>
                <div class="stat-card">
                    <h4>Error Rate</h4>
                    <div class="stat-value">{error_rate:.1%}</div>
                </div>
                <div class="stat-card">
                    <h4>Affected Tools</h4>
                    <div class="stat-value">{affected_tools}</div>
                </div>
                <div class="stat-card">
                    <h4>Error Categories</h4>
                    <div class="stat-value">{failures['error_category'].nunique()}</div>
                </div>
            </div>
        """

        # Primary failure modes analysis
        html += """
            <div class="failure-modes">
                <h4>🚨 Primary Failure Modes</h4>
        """

        if 'ActionCheckFailure' in failures['error_category'].values:
            action_failures = failures[failures['error_category'] == 'ActionCheckFailure']
            html += f"""
                <div class="failure-mode">
                    <h5>Action Check Failures</h5>
                    <p><strong>{len(action_failures)} tools</strong> failed action validation checks:</p>
                    <ul>
            """
            for _, row in action_failures.iterrows():
                html += f"""
                    <li><strong>{row['tool_name']}</strong>: {int(row['count'])} failures ({row['failure_rate']:.1%} rate)
                """
                if 'simulations_affected' in failures.columns:
                    html += f"<br>→ Affected {row['simulations_affected']} simulation(s)"
                if 'example_args' in failures.columns:
                    html += f"<br>→ Example args: <code>{row['example_args']}</code>"
                html += "</li>"
            html += "</ul></div>"

        # Performance impact analysis
        html += """
            <div class="performance-impact">
                <h4>⚡ Performance Impact Analysis</h4>
        """

        if not tool_perf.empty:
            # High usage tools with poor performance
            high_usage_tools = tool_perf[tool_perf['total_calls'] >= 5]
            poor_performers = high_usage_tools[high_usage_tools['performance_category'] == 'poor']

            if not poor_performers.empty:
                html += """
                    <div class="poor-performers">
                        <h5>High-Usage Tools with Poor Performance</h5>
                        <table class="performance-table">
                            <thead>
                                <tr>
                                    <th>Tool Name</th>
                                    <th>Total Calls</th>
                                    <th>Success Rate</th>
                                    <th>Avg Time (ms)</th>
                                </tr>
                            </thead>
                            <tbody>
                """
                for _, row in poor_performers.iterrows():
                    html += f"""
                        <tr>
                            <td><strong>{row['tool_name']}</strong></td>
                            <td>{int(row['total_calls'])}</td>
                            <td>{row['success_rate']:.1%}</td>
                            <td>{row['avg_execution_time']*1000:.2f}ms</td>
                        </tr>
                    """
                html += "</tbody></table></div>"

            # Slowest tools analysis
            slowest_tools = tool_perf.nlargest(5, 'avg_execution_time')
            html += """
                <div class="slowest-tools">
                    <h5>Slowest Tools by Execution Time</h5>
                    <table class="performance-table">
                        <thead>
                            <tr>
                                <th>Tool Name</th>
                                <th>Avg Time (ms)</th>
                                <th>Total Calls</th>
                                <th>Success Rate</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            for _, row in slowest_tools.iterrows():
                html += f"""
                    <tr>
                        <td><strong>{row['tool_name']}</strong></td>
                        <td>{row['avg_execution_time']*1000:.2f}ms</td>
                        <td>{int(row['total_calls'])}</td>
                        <td>{row['success_rate']:.1%}</td>
                    </tr>
                """
            html += "</tbody></table></div>"

        html += "</div>"  # Close performance-impact

        # Key insights and recommendations
        html += """
            <div class="failure-insights">
                <h4>💡 Key Insights</h4>
                <ul>
        """

        # Most problematic tool
        if not failures.empty:
            most_failed_tool = failures.loc[failures['count'].idxmax(), 'tool_name']
            most_failed_count = failures['count'].max()
            html += f"<li><strong>Most problematic tool:</strong> {most_failed_tool} ({most_failed_count} failures)</li>"

            if 'ActionCheckFailure' in failures['error_category'].values:
                html += "<li><strong>Primary failure mode:</strong> Action validation failures suggest issues with tool argument validation or execution logic</li>"

            # Success rate analysis
            if not tool_perf.empty:
                avg_success_rate = tool_perf['success_rate'].mean()
                html += f"<li><strong>Average tool success rate:</strong> {avg_success_rate:.1%}</li>"

                if avg_success_rate < 0.8:
                    html += "<li><strong>⚠️ Low overall success rate</strong> suggests systemic issues requiring investigation</li>"

        html += "</ul></div>"

        # Critical recommendations
        html += """
            <div class="recommendations">
                <h4>🔧 Critical Recommendations</h4>
                <ol>
        """

        if not failures.empty:
            # Specific recommendations based on failure patterns
            if 'ActionCheckFailure' in failures['error_category'].values:
                html += "<li><strong>Action Validation:</strong> Review and strengthen argument validation logic for failing tools</li>"
                html += "<li><strong>Error Handling:</strong> Implement more robust error recovery mechanisms</li>"

            if not tool_perf.empty and len(tool_perf[tool_perf['performance_category'] == 'poor']) > 0:
                html += "<li><strong>Performance Optimization:</strong> Focus on improving poor-performing tools with high usage</li>"

            html += "<li><strong>Monitoring:</strong> Implement enhanced monitoring and alerting for tools with high failure rates</li>"
            html += "<li><strong>Testing:</strong> Increase test coverage for identified problematic tool patterns</li>"

        html += "</ol></div>"

        html += "</div></div>"  # Close failure-modes and failure-section

        return html

    def _generate_task_simulation_analysis_md(self, summary, tool_perf, state_analysis) -> str:
        """Generate task and simulation analysis section."""
        md_content = "\n---\n\n## 🎯 Task & Simulation Analysis\n\n"

        # Simulation success analysis
        total_sims = summary.get('total_simulations', 0)
        successful_sims = summary.get('successful_simulations', 0)
        failed_sims = total_sims - successful_sims

        md_content += f"### 📊 Simulation Performance Breakdown\n\n"
        md_content += f"- **Total simulations executed:** {total_sims}\n"
        md_content += f"- **Successful completions:** {successful_sims} ({successful_sims/total_sims*100:.1f}%)\n"
        md_content += f"- **Failed simulations:** {failed_sims} ({failed_sims/total_sims*100:.1f}%)\n"

        if failed_sims > 0:
            md_content += f"\n**Failure Impact Analysis:**\n"
            md_content += f"- Each failure represents a complete task breakdown\n"
            md_content += f"- {failed_sims/total_sims*100:.1f}% of tasks could not be completed successfully\n"

            # Estimate impact based on action vs non-action tasks
            if not tool_perf.empty:
                state_changing_tools = len(tool_perf[tool_perf['state_change_rate'] > 0])
                if state_changing_tools > 0:
                    md_content += f"- {state_changing_tools} tools perform state-changing operations\n"
                    md_content += f"- Failures likely impact real-world task completion\n"

        # Success metrics analysis
        success_source = summary.get('success_metric_source', 'unknown')
        md_content += f"\n### 🎖️ Success Measurement\n\n"
        md_content += f"- **Success metric source:** {success_source}\n"

        if success_source == 'action_checks':
            md_content += f"- Success determined by **action validation checks**\n"
            md_content += f"- This measures whether the agent performed the correct actions with correct parameters\n"
            md_content += f"- More reliable than execution-based success metrics\n"
            md_content += f"- Failures indicate logical/reasoning issues rather than technical problems\n"
        elif success_source == 'execution_success':
            md_content += f"- Success determined by **tool execution success**\n"
            md_content += f"- This measures whether tool calls completed without errors\n"
            md_content += f"- May miss logical errors if tools execute but with wrong parameters\n"

        # Task complexity indicators
        md_content += f"\n### 🔧 Task Complexity Indicators\n\n"

        if not tool_perf.empty:
            total_calls = tool_perf['total_calls'].sum()
            avg_calls_per_sim = total_calls / total_sims if total_sims > 0 else 0
            unique_tools = len(tool_perf)
            state_changing_calls = summary.get('state_changing_calls', 0)

            md_content += f"- **Average tool calls per simulation:** {avg_calls_per_sim:.1f}\n"
            md_content += f"- **Unique tools used:** {unique_tools}\n"
            md_content += f"- **State-changing operations:** {state_changing_calls} ({state_changing_calls/total_calls*100:.1f}% of all calls)\n"

            # Complexity assessment
            if avg_calls_per_sim > 15:
                complexity = "High"
                md_content += f"- **Complexity level:** {complexity} (>15 calls/simulation suggests complex multi-step tasks)\n"
            elif avg_calls_per_sim > 8:
                complexity = "Medium"
                md_content += f"- **Complexity level:** {complexity} (8-15 calls/simulation indicates moderate complexity)\n"
            else:
                complexity = "Low"
                md_content += f"- **Complexity level:** {complexity} (<8 calls/simulation suggests simple tasks)\n"

            # Tool diversity analysis
            most_used_tool_calls = tool_perf['total_calls'].max()
            tool_usage_concentration = most_used_tool_calls / total_calls * 100

            md_content += f"\n**Tool Usage Patterns:**\n"
            md_content += f"- **Most used tool concentration:** {tool_usage_concentration:.1f}% of all calls\n"

            if tool_usage_concentration > 50:
                md_content += f"- **High concentration** suggests tasks heavily depend on one tool type\n"
            elif tool_usage_concentration > 30:
                md_content += f"- **Moderate concentration** indicates some tools are more critical than others\n"
            else:
                md_content += f"- **Distributed usage** suggests balanced tool utilization\n"

        return md_content

    def _generate_performance_deep_dive_md(self, tool_perf, sequence_analysis) -> str:
        """Generate detailed performance analysis section."""
        md_content = "\n---\n\n## ⚡ Performance Deep Dive\n\n"

        if tool_perf.empty:
            md_content += "No performance data available for analysis.\n"
            return md_content

        # Performance tier analysis
        excellent_tools = tool_perf[tool_perf['performance_category'] == 'excellent']
        good_tools = tool_perf[tool_perf['performance_category'] == 'good']
        fair_tools = tool_perf[tool_perf['performance_category'] == 'fair']
        poor_tools = tool_perf[tool_perf['performance_category'] == 'poor']

        md_content += f"### 🏆 Performance Tier Analysis\n\n"

        for tier, tools_df, description in [
            ("Excellent", excellent_tools, "High success rate (≥95%) and fast execution (≤1s)"),
            ("Good", good_tools, "Good success rate (≥90%) and reasonable execution (≤2s)"),
            ("Fair", fair_tools, "Acceptable success rate (≥75%)"),
            ("Poor", poor_tools, "Low success rate (<75%)")
        ]:
            if not tools_df.empty:
                md_content += f"**{tier} Performance ({len(tools_df)} tools)** - {description}:\n"
                for _, tool in tools_df.iterrows():
                    md_content += f"- `{tool['tool_name']}`: {tool['success_rate']:.1%} success, {tool['avg_execution_time']*1000:.2f}ms avg time, {int(tool['total_calls'])} calls\n"
                md_content += f"\n"

        # Critical performance issues
        if not poor_tools.empty:
            md_content += f"### 🚨 Critical Performance Issues\n\n"
            high_usage_poor = poor_tools[poor_tools['total_calls'] >= 5]

            if not high_usage_poor.empty:
                md_content += f"**High-Usage Poor Performers** (≥5 calls with poor performance):\n\n"
                for _, tool in high_usage_poor.iterrows():
                    impact_score = tool['total_calls'] * (1 - tool['success_rate'])
                    md_content += f"- **`{tool['tool_name']}`**:\n"
                    md_content += f"  - Success rate: {tool['success_rate']:.1%}\n"
                    md_content += f"  - Total calls: {int(tool['total_calls'])}\n"
                    md_content += f"  - Failed calls: {int(tool['total_calls'] * (1 - tool['success_rate']))}\n"
                    md_content += f"  - Impact score: {impact_score:.1f} (calls × failure rate)\n"
                    md_content += f"  - State changing: {'Yes' if tool['state_change_rate'] > 0 else 'No'}\n"
                md_content += f"\n"

        # Execution time analysis
        md_content += f"### ⏱️ Execution Time Analysis\n\n"

        avg_time = tool_perf['avg_execution_time'].mean()
        median_time = tool_perf['avg_execution_time'].median()
        slowest_tool = tool_perf.loc[tool_perf['avg_execution_time'].idxmax()]
        fastest_tool = tool_perf.loc[tool_perf['avg_execution_time'].idxmin()]

        md_content += f"- **Average execution time across all tools:** {avg_time*1000:.2f}ms\n"
        md_content += f"- **Median execution time:** {median_time*1000:.2f}ms\n"
        md_content += f"- **Slowest tool:** `{slowest_tool['tool_name']}` ({slowest_tool['avg_execution_time']*1000:.2f}ms)\n"
        md_content += f"- **Fastest tool:** `{fastest_tool['tool_name']}` ({fastest_tool['avg_execution_time']*1000:.2f}ms)\n"

        # Performance vs usage correlation
        md_content += f"\n**Performance vs Usage Correlation:**\n"

        # High usage tools analysis
        high_usage = tool_perf[tool_perf['total_calls'] >= 10]
        if not high_usage.empty:
            avg_success_high_usage = high_usage['success_rate'].mean()
            md_content += f"- High-usage tools (≥10 calls) average success rate: {avg_success_high_usage:.1%}\n"

        low_usage = tool_perf[tool_perf['total_calls'] < 10]
        if not low_usage.empty:
            avg_success_low_usage = low_usage['success_rate'].mean()
            md_content += f"- Low-usage tools (<10 calls) average success rate: {avg_success_low_usage:.1%}\n"

            if not high_usage.empty:
                performance_correlation = avg_success_high_usage - avg_success_low_usage
                if abs(performance_correlation) > 0.1:
                    direction = "better" if performance_correlation > 0 else "worse"
                    md_content += f"- **Usage-performance correlation:** High-usage tools perform {abs(performance_correlation)*100:.1f}% {direction}\n"

        # State-changing vs read-only performance
        state_changing = tool_perf[tool_perf['state_change_rate'] > 0]
        read_only = tool_perf[tool_perf['state_change_rate'] == 0]

        if not state_changing.empty and not read_only.empty:
            md_content += f"\n**State-Changing vs Read-Only Performance:**\n"
            state_avg_success = state_changing['success_rate'].mean()
            readonly_avg_success = read_only['success_rate'].mean()
            state_avg_time = state_changing['avg_execution_time'].mean()
            readonly_avg_time = read_only['avg_execution_time'].mean()

            md_content += f"- State-changing tools: {state_avg_success:.1%} success, {state_avg_time:.4f}s avg time\n"
            md_content += f"- Read-only tools: {readonly_avg_success:.1%} success, {readonly_avg_time:.4f}s avg time\n"

            if state_avg_success < readonly_avg_success - 0.1:
                md_content += f"- ⚠️ State-changing tools show {(readonly_avg_success - state_avg_success)*100:.1f}% lower success rate\n"

        return md_content

    def _generate_execution_patterns_md(self, summary, tool_perf, sequence_analysis) -> str:
        """Generate execution patterns and workflow analysis."""
        md_content = "\n---\n\n## 🔄 Execution Patterns & Workflow Analysis\n\n"

        # Execution timeline analysis
        execution_timespan = summary.get('execution_timespan', 0)
        total_execution_time = summary.get('total_execution_time', 0)
        total_calls = summary.get('total_tool_calls', 0)

        md_content += f"### ⏰ Execution Timeline\n\n"
        md_content += f"- **Total execution timespan:** {execution_timespan:.1f} seconds\n"
        md_content += f"- **Actual tool execution time:** {total_execution_time:.4f} seconds\n"
        md_content += f"- **Execution efficiency:** {(total_execution_time/execution_timespan)*100:.2f}% (time spent in tool execution)\n"

        if execution_timespan > 0:
            calls_per_second = total_calls / execution_timespan
            md_content += f"- **Average call rate:** {calls_per_second:.2f} calls/second\n"

            if calls_per_second > 2:
                md_content += f"- **High call rate** suggests rapid sequential execution\n"
            elif calls_per_second < 0.5:
                md_content += f"- **Low call rate** may indicate thinking/processing time between calls\n"

        # Tool sequence patterns
        md_content += f"\n### 🔗 Tool Usage Patterns\n\n"

        if not sequence_analysis.empty:
            md_content += f"**Most Common Tool Transitions:**\n\n"

            # Analyze top transitions
            top_transitions = sequence_analysis.head(5)
            for _, row in top_transitions.iterrows():
                source, target, count = row['source'], row['target'], int(row['count'])

                if source == target:
                    md_content += f"- **`{source}` → `{target}`** ({count}x): Self-loops indicate repeated calls to same tool\n"
                else:
                    md_content += f"- **`{source}` → `{target}`** ({count}x): Common workflow pattern\n"

            # Pattern analysis
            total_transitions = sequence_analysis['count'].sum()
            top_transition_count = sequence_analysis.iloc[0]['count']
            concentration = (top_transition_count / total_transitions) * 100

            md_content += f"\n**Pattern Analysis:**\n"
            md_content += f"- **Most common transition:** {concentration:.1f}% of all transitions\n"

            if concentration > 40:
                md_content += f"- **Highly concentrated** workflow with dominant pattern\n"
            elif concentration > 20:
                md_content += f"- **Moderately concentrated** workflow with some preferred patterns\n"
            else:
                md_content += f"- **Distributed** workflow with varied patterns\n"

            # Self-loop analysis
            self_loops = sequence_analysis[sequence_analysis['source'] == sequence_analysis['target']]
            if not self_loops.empty:
                total_self_loops = self_loops['count'].sum()
                self_loop_rate = (total_self_loops / total_transitions) * 100
                md_content += f"- **Self-loop rate:** {self_loop_rate:.1f}% of transitions are repeated calls to same tool\n"

                if self_loop_rate > 30:
                    md_content += f"- **High self-loop rate** may indicate retry logic or iterative processing\n"

        # Workflow insights
        md_content += f"\n### 🧠 Workflow Intelligence\n\n"

        if not tool_perf.empty:
            # Tool diversity
            unique_tools = len(tool_perf)
            total_calls = tool_perf['total_calls'].sum()
            avg_calls_per_tool = total_calls / unique_tools

            md_content += f"- **Tool diversity:** {unique_tools} unique tools used\n"
            md_content += f"- **Average calls per tool:** {avg_calls_per_tool:.1f}\n"

            # Usage distribution
            top_tool_usage = tool_perf['total_calls'].max()
            usage_concentration = (top_tool_usage / total_calls) * 100

            md_content += f"- **Usage concentration:** {usage_concentration:.1f}% of calls go to most-used tool\n"

            if usage_concentration > 60:
                md_content += f"- **Tool dependency:** Workflow heavily depends on one primary tool\n"
            elif usage_concentration < 30:
                md_content += f"- **Balanced usage:** Well-distributed tool utilization\n"

        # Success pattern analysis
        total_sims = summary.get('total_simulations', 0)
        successful_sims = summary.get('successful_simulations', 0)

        if total_sims > 0 and successful_sims != total_sims:
            md_content += f"\n### 🎯 Success Pattern Analysis\n\n"

            success_rate = successful_sims / total_sims

            if success_rate >= 0.8:
                md_content += f"- **High success pattern** ({success_rate:.1%}): Consistent execution with occasional failures\n"
            elif success_rate >= 0.5:
                md_content += f"- **Moderate success pattern** ({success_rate:.1%}): Mixed results requiring investigation\n"
            else:
                md_content += f"- **Low success pattern** ({success_rate:.1%}): Systematic issues affecting most executions\n"

            # Estimate failure clustering
            failed_sims = total_sims - successful_sims
            if failed_sims > 1:
                md_content += f"- **Failure distribution:** {failed_sims} failed simulations out of {total_sims} total\n"
                if failed_sims == 1:
                    md_content += f"- **Isolated failure:** Single failure suggests edge case or random error\n"
                elif failed_sims == total_sims - successful_sims and successful_sims > 0:
                    md_content += f"- **Mixed pattern:** Both successes and failures indicate inconsistent behavior\n"

        return md_content

    def _generate_advanced_failure_patterns_md(self, summary, failures, tool_perf) -> str:
        """Generate advanced failure pattern analysis similar to the requested format."""
        md_content = "\n---\n\n## 🎯 Performance Issues Analysis\n\n"

        total_calls = summary.get('total_tool_calls', 0)
        total_failures = summary.get('failed_calls', 0) if failures.empty else failures['count'].sum()
        success_rate = summary.get('tool_success_rate', 0)

        # Overall performance assessment
        md_content += f"### Overall Performance Assessment\n\n"
        if success_rate >= 0.9:
            md_content += f"- **Overall success: {success_rate:.1%} (excellent)**\n"
        elif success_rate >= 0.7:
            md_content += f"- **Overall success: {success_rate:.1%} (good)**\n"
        elif success_rate >= 0.5:
            md_content += f"- **Overall success: {success_rate:.1%} (concerning)**\n"
        else:
            md_content += f"- **Overall success: {success_rate:.1%} (critical)**\n"

        # Analyze action vs read-only performance
        if not tool_perf.empty:
            state_changing = tool_perf[tool_perf['state_change_rate'] > 0]
            read_only = tool_perf[tool_perf['state_change_rate'] == 0]

            if not state_changing.empty and not read_only.empty:
                state_avg_success = state_changing['success_rate'].mean()
                read_avg_success = read_only['success_rate'].mean()

                md_content += f"- **State-changing actions accuracy: {state_avg_success:.1%}**\n"
                md_content += f"- **Read-only actions accuracy: {read_avg_success:.1%}**\n"

                if state_avg_success < 0.5:
                    md_content += f"- **Critical**: State-changing actions show severe accuracy issues\n"

                performance_drop = read_avg_success - state_avg_success
                if performance_drop > 0.2:
                    md_content += f"- **{performance_drop:.0%}pp performance drop when actions are required** ({read_avg_success:.1%} → {state_avg_success:.1%} success)\n"

        # Action complexity impact
        if not failures.empty:
            md_content += f"\n### 🔍 Failure Patterns\n\n"

            total_failure_rate = total_failures / total_calls if total_calls > 0 else 0
            md_content += f"- **{total_failure_rate:.0%} of operations result in failures**\n"

            # Most failed actions
            top_failures = failures.nlargest(3, 'count')
            if not top_failures.empty:
                md_content += f"- **Most failed operations:**\n"
                for _, row in top_failures.iterrows():
                    failure_percentage = row['failure_rate'] * 100
                    md_content += f"  - {row['tool_name']}: {failure_percentage:.0f}% failure rate\n"

            # Database validation patterns
            action_check_failures = failures[failures['error_category'] == 'ActionCheckFailure']
            if not action_check_failures.empty:
                md_content += f"- **Action validation failures in {len(action_check_failures)} different tools**\n"
                total_action_failures = action_check_failures['count'].sum()
                action_failure_rate = total_action_failures / total_failures if total_failures > 0 else 0
                md_content += f"- **{action_failure_rate:.0%}% of failures involve validation mismatches**\n"

        # Performance degradation patterns
        if not tool_perf.empty:
            md_content += f"\n### 📊 Action Complexity Impact\n\n"

            # Categorize tools by complexity (approximated by state changes)
            no_action_tools = tool_perf[tool_perf['state_change_rate'] == 0]
            action_tools = tool_perf[tool_perf['state_change_rate'] > 0]

            if not no_action_tools.empty:
                no_action_success = no_action_tools['success_rate'].mean()
                md_content += f"- **0 state changes: {no_action_success:.1%} success**\n"

            if not action_tools.empty:
                action_success = action_tools['success_rate'].mean()
                md_content += f"- **Tools with state changes: {action_success:.1%} success**\n"

                if not no_action_tools.empty and no_action_success - action_success > 0.2:
                    md_content += f"- **Clear correlation between complexity and failure**\n"

        return md_content

    def _generate_communication_analysis_md(self, summary, tool_perf, sequence_analysis) -> str:
        """Analyze communication patterns vs tool call patterns."""
        md_content = "\n---\n\n## 💬 Communication vs Tool Call Analysis\n\n"

        # Look for transfer patterns
        transfer_tools = tool_perf[tool_perf['tool_name'].str.contains('transfer|human', case=False, na=False)]
        communication_tools = tool_perf[tool_perf['tool_name'].str.contains('send|message|communicate', case=False, na=False)]

        total_calls = summary.get('total_tool_calls', 0)

        if not transfer_tools.empty:
            transfer_calls = transfer_tools['total_calls'].sum()
            transfer_rate = (transfer_calls / total_calls * 100) if total_calls > 0 else 0
            md_content += f"### Transfer to Human Analysis\n\n"
            md_content += f"- **Transfer calls: {transfer_calls} ({transfer_rate:.1f}% of total calls)**\n"

            avg_transfer_success = transfer_tools['success_rate'].mean()
            md_content += f"- **Transfer success rate: {avg_transfer_success:.1%}**\n"

            if transfer_rate > 20:
                md_content += f"- **High transfer rate** may indicate agent limitations or complex user requests\n"

        if not communication_tools.empty:
            comm_calls = communication_tools['total_calls'].sum()
            comm_rate = (comm_calls / total_calls * 100) if total_calls > 0 else 0
            md_content += f"\n### Communication Tool Usage\n\n"
            md_content += f"- **Communication calls: {comm_calls} ({comm_rate:.1f}% of total calls)**\n"

            avg_comm_success = communication_tools['success_rate'].mean()
            md_content += f"- **Communication success rate: {avg_comm_success:.1%}**\n"

        # Analyze termination patterns from summary
        md_content += f"\n### 🛑 Task Termination Analysis\n\n"

        # Look for stopping patterns
        execution_timespan = summary.get('execution_timespan', 0)
        total_execution_time = summary.get('total_execution_time', 0)

        if execution_timespan > 0:
            efficiency = (total_execution_time / execution_timespan) * 100
            md_content += f"- **Execution efficiency: {efficiency:.1f}%** (time spent in actual tool execution)\n"

            if efficiency < 1:
                md_content += f"- **Low efficiency suggests high wait times** or communication delays\n"

        # Max length analysis (approximate from data patterns)
        if not tool_perf.empty:
            high_call_tools = tool_perf[tool_perf['total_calls'] >= 10]
            if not high_call_tools.empty:
                md_content += f"- **{len(high_call_tools)} tools used extensively** (10+ calls each)\n"
                md_content += f"- **Possible indication of retry patterns** or complex multi-step operations\n"

        return md_content

    def _generate_task_simulation_analysis_md(self, summary, tool_perf, state_analysis) -> str:
        """Generate task and simulation success analysis with trial patterns."""
        md_content = "\n---\n\n## 📋 Task & Simulation Analysis\n\n"

        # Simulation success patterns
        total_sims = summary.get('total_simulations', 0)
        successful_sims = summary.get('successful_simulations', 0)
        task_success_rate = summary.get('task_success_rate', 0)

        md_content += f"### Simulation Success Patterns\n\n"
        if total_sims > 0:
            md_content += f"- **Total simulations: {total_sims}**\n"
            md_content += f"- **Successful simulations: {successful_sims}**\n"
            md_content += f"- **Task success rate: {task_success_rate:.1%}**\n"

            if task_success_rate >= 0.8:
                md_content += f"- **Excellent task completion rate** - System performing well\n"
            elif task_success_rate >= 0.6:
                md_content += f"- **Good task completion rate** - Some optimization opportunities\n"
            elif task_success_rate >= 0.4:
                md_content += f"- **Moderate task completion rate** - Significant improvement needed\n"
            else:
                md_content += f"- **Poor task completion rate** - Critical issues require attention\n"

        # Trial analysis (if multiple trials available)
        md_content += f"\n### 📈 Trial Performance Patterns\n\n"

        # Success metric source analysis
        success_metric_source = summary.get('success_metric_source', 'unknown')
        md_content += f"- **Success evaluation method: {success_metric_source}**\n"

        if success_metric_source == 'action_checks':
            md_content += f"- **Action-based evaluation** - Success determined by correct action execution\n"
        elif success_metric_source == 'db_checks':
            md_content += f"- **Database validation** - Success based on database state consistency\n"
        elif success_metric_source == 'communicate_checks':
            md_content += f"- **Communication-based** - Success based on proper information exchange\n"

        # Tool complexity vs success correlation
        if not tool_perf.empty and total_sims > 0:
            md_content += f"\n### 🎲 Complexity vs Success Correlation\n\n"

            # Calculate complexity metrics
            unique_tools_used = len(tool_perf)
            total_tool_calls = summary.get('total_tool_calls', 0)
            avg_tools_per_sim = unique_tools_used / total_sims if total_sims > 0 else 0
            avg_calls_per_sim = total_tool_calls / total_sims if total_sims > 0 else 0

            md_content += f"- **Average tools per simulation: {avg_tools_per_sim:.1f}**\n"
            md_content += f"- **Average calls per simulation: {avg_calls_per_sim:.1f}**\n"

            # State changing vs read-only impact
            if not state_analysis.empty:
                state_changing = state_analysis[state_analysis['state_changed'] == True]
                if not state_changing.empty:
                    state_calls = state_changing['total_calls'].sum()
                    state_call_rate = (state_calls / total_tool_calls * 100) if total_tool_calls > 0 else 0
                    md_content += f"- **State-changing operations: {state_call_rate:.1f}% of all calls**\n"

                    if task_success_rate < 0.5 and state_call_rate > 20:
                        md_content += f"- **High state-change rate with low success** suggests action execution issues\n"

        return md_content

    def _generate_key_insights_md(self, summary, tool_perf, failures, state_analysis, sequence_analysis) -> list:
        """Generate key insights in markdown format."""
        insights = []

        # Performance insights
        if not tool_perf.empty:
            excellent_tools = len(tool_perf[tool_perf['performance_category'] == 'excellent'])
            poor_tools = len(tool_perf[tool_perf['performance_category'] == 'poor'])
            most_used = tool_perf.iloc[0]['tool_name'] if len(tool_perf) > 0 else "N/A"

            insights.append(f"**{excellent_tools}** out of {len(tool_perf)} tools have excellent performance (≥95% success rate)")
            insights.append(f"**{most_used}** is the most frequently used tool with {tool_perf.iloc[0]['total_calls']} calls")
            insights.append(f"Overall system reliability: **{summary.get('tool_success_rate', 0):.1%}**")

            if poor_tools > 0:
                insights.append(f"**{poor_tools}** tools showing poor performance require attention")

        # Failure insights
        if not failures.empty:
            total_failures = failures['count'].sum()
            total_calls = summary.get('total_tool_calls', 0)
            error_rate = (total_failures / total_calls * 100) if total_calls > 0 else 0

            insights.append(f"**{error_rate:.1f}%** error rate across all tool executions")

            most_failed = failures.iloc[0]['tool_name'] if len(failures) > 0 else "N/A"
            insights.append(f"**{most_failed}** has the highest failure count with {failures.iloc[0]['count']} failures")

            if 'ActionCheckFailure' in failures['error_category'].values:
                action_failures = failures[failures['error_category'] == 'ActionCheckFailure']['count'].sum()
                insights.append(f"**{action_failures}** failures are due to action validation issues")

        # State change insights
        if not state_analysis.empty:
            state_changing = len(state_analysis[state_analysis['state_changed'] == True])
            read_only = len(state_analysis[state_analysis['state_changed'] == False])

            insights.append(f"Tool distribution: **{state_changing}** state-changing, **{read_only}** read-only")

            if state_changing > 0 and read_only > 0:
                state_tools = state_analysis[state_analysis['state_changed'] == True]
                read_tools = state_analysis[state_analysis['state_changed'] == False]
                state_avg_success = state_tools['success_rate'].mean()
                read_avg_success = read_tools['success_rate'].mean()

                if state_avg_success < read_avg_success - 0.1:
                    insights.append(f"State-changing tools underperform read-only tools ({state_avg_success:.1%} vs {read_avg_success:.1%})")

        # Sequence insights
        if not sequence_analysis.empty:
            total_transitions = sequence_analysis['count'].sum()
            self_loops = sequence_analysis[sequence_analysis['source'] == sequence_analysis['target']]['count'].sum()
            self_loop_rate = (self_loops / total_transitions * 100) if total_transitions > 0 else 0

            if self_loop_rate > 30:
                insights.append(f"High self-loop rate ({self_loop_rate:.1f}%) indicates potential retry patterns")

            top_transition = sequence_analysis.iloc[0] if len(sequence_analysis) > 0 else None
            if top_transition is not None:
                insights.append(f"Most common pattern: **{top_transition['source']}** → **{top_transition['target']}** ({top_transition['count']} times)")

        return insights

    def _generate_recommendations_md(self, summary, tool_perf, failures, state_analysis) -> list:
        """Generate recommendations in markdown format."""
        recommendations = []

        # Performance recommendations
        if not tool_perf.empty:
            poor_performers = tool_perf[tool_perf['performance_category'] == 'poor']
            if not poor_performers.empty:
                high_usage_poor = poor_performers[poor_performers['total_calls'] >= 10]
                if not high_usage_poor.empty:
                    recommendations.append(f"**High Impact Pattern**: High-usage poor performers identified: {', '.join(high_usage_poor['tool_name'].tolist())}")

                recommendations.append(f"**Performance Pattern**: {len(poor_performers)} tools categorized as poor performers based on execution metrics")

        # Failure recommendations
        if not failures.empty:
            action_check_failures = failures[failures['error_category'] == 'ActionCheckFailure']
            if not action_check_failures.empty:
                failure_count = len(action_check_failures)
                recommendations.append(f"**Action Check Pattern**: {failure_count} action validation failures detected across tool executions")

            high_failure_tools = failures[failures['failure_rate'] > 0.5]
            if not high_failure_tools.empty:
                tool_names = ', '.join(high_failure_tools['tool_name'].tolist())
                recommendations.append(f"**High Failure Rate**: Tools with >50% failure rate detected: {tool_names}")

        # State change recommendations
        if not state_analysis.empty:
            state_changing = state_analysis[state_analysis['state_changed'] == True]
            if not state_changing.empty:
                low_success_state = state_changing[state_changing['success_rate'] < 0.7]
                if not low_success_state.empty:
                    low_count = len(low_success_state)
                    avg_success = low_success_state['success_rate'].mean()
                    recommendations.append(f"**State Operation Pattern**: {low_count} state-changing operations show {avg_success:.1%} average success rate")

        # General recommendations based on success rates
        tool_success_rate = summary.get('tool_success_rate', 0)
        if tool_success_rate < 0.8:
            recommendations.append(f"**System Status**: Overall tool success rate at {tool_success_rate:.1%} indicates significant reliability challenges")
        elif tool_success_rate < 0.95:
            recommendations.append(f"**Performance Analysis**: Tool success rate at {tool_success_rate:.1%} indicates potential optimization opportunities")

        task_success_rate = summary.get('task_success_rate', 0)
        if task_success_rate < 0.7:
            recommendations.append(f"**Task Analysis**: Task completion rate at {task_success_rate:.1%} indicates workflow execution challenges")

        return recommendations

    def create_enhanced_analysis_report(self, output_path: str, log_file_name: str = "execution_logs") -> str:
        """
        Create an enhanced HTML report that combines comprehensive analysis content
        with interactive plots, similar to analysis_report.md but in HTML format.
        """
        from datetime import datetime
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # Get all analysis data
        summary = self.analyzer.get_summary_metrics()
        tool_perf = self.analyzer.get_tool_performance()
        failures = self.analyzer.get_failure_analysis()
        state_analysis = self.analyzer.get_state_change_analysis()
        sequence_analysis = self.analyzer.get_tool_sequence_analysis()

        # Generate insights and recommendations for HTML
        insights = self._generate_key_insights(summary, tool_perf, failures, state_analysis, sequence_analysis)
        recommendations = self._generate_recommendations(summary, tool_perf, failures, state_analysis)

        # Create summary dashboard
        summary_html = self.create_summary_dashboard(include_task_success=True).to_html(full_html=False, include_plotlyjs=False)

        # Create performance issues analysis plot
        perf_issues_html = self._create_performance_issues_plot(summary, tool_perf, failures).to_html(full_html=False, include_plotlyjs=False)

        # Create communication analysis plot
        comm_analysis_html = self._create_communication_analysis_plot(summary, tool_perf, sequence_analysis).to_html(full_html=False, include_plotlyjs=False)

        # Create execution patterns plot
        exec_patterns_html = self._create_execution_patterns_plot(summary, tool_perf, sequence_analysis).to_html(full_html=False, include_plotlyjs=False)

        # Create task success correlation plot
        task_analysis_html = self._create_task_analysis_plot(summary, tool_perf, state_analysis).to_html(full_html=False, include_plotlyjs=False)

        # Build comprehensive HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Tau2 Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        @media print {{
            .no-print {{ display: none; }}
            .page-break {{ page-break-before: always; }}
            body {{ font-size: 12px; }}
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }}

        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
            font-weight: 300;
        }}

        .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .section {{
            margin: 30px 0;
            padding: 25px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border-left: 4px solid #007bff;
        }}

        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
            margin-top: 0;
        }}

        .section h3 {{
            color: #34495e;
            margin-top: 25px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .metric-card {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .metric-value {{
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .plot-container {{
            margin: 30px 0;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }}

        .insight-box {{
            background: #f8f9ff;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}

        .insight-box h4 {{
            color: #2c3e50;
            margin-top: 0;
        }}

        .insight-box ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}

        .insight-box li {{
            margin-bottom: 8px;
        }}

        .recommendations {{
            background: #f3e5f5;
            border: 1px solid #e1bee7;
            border-radius: 8px;
            padding: 20px;
        }}

        .recommendations ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}

        .recommendations li {{
            margin-bottom: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}

        th {{
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        .status-excellent {{ color: #28a745; font-weight: bold; }}
        .status-good {{ color: #17a2b8; font-weight: bold; }}
        .status-fair {{ color: #ffc107; font-weight: bold; }}
        .status-poor {{ color: #dc3545; font-weight: bold; }}

        .analysis-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}

        .analysis-card {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
        }}

        .performance-issue {{
            background: #fff5f5;
            border: 1px solid #fed7d7;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}

        .performance-good {{
            background: #f0fff4;
            border: 1px solid #c6f6d5;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}

        .key-metric {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🚀 Enhanced Tau2 Analysis Report</h1>
            <div class="subtitle">
                Comprehensive performance analysis with interactive visualizations<br>
                Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}<br>
                Source: <strong>{log_file_name}</strong>
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{summary.get('total_simulations', 'N/A')}</div>
                    <div class="metric-label">Total Simulations</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('total_trials', 'N/A')}</div>
                    <div class="metric-label">Total Trials</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('total_tasks', 'N/A')}</div>
                    <div class="metric-label">Total Tasks</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('total_tool_calls', 0)}</div>
                    <div class="metric-label">Total Tool Calls</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('tools_used', 0)}</div>
                    <div class="metric-label">Unique Tools</div>
                </div>
            </div>
            <div class="plot-container">
                {summary_html}
            </div>
        </div>

        <!-- Key Insights -->
        <div class="section">
            <h2>💡 Key Insights & Recommendations</h2>
            <div class="analysis-grid">
                <div class="analysis-card">
                    <h3>🔍 Key Insights</h3>
                    {insights}
                </div>
                <div class="analysis-card">
                    <h3>💡 Recommendations</h3>
                    <div class="recommendations">
                        {recommendations}
                    </div>
                </div>
            </div>
        </div>

        <!-- Performance Issues Analysis -->
        <div class="section page-break">
            <h2>🎯 Performance Issues Analysis</h2>
            <div class="plot-container">
                {perf_issues_html}
            </div>
            {self._generate_performance_issues_analysis_html(summary, tool_perf, failures)}
        </div>

        <!-- Communication vs Tool Call Analysis -->
        <div class="section page-break">
            <h2>💬 Communication vs Tool Call Analysis</h2>
            <div class="plot-container">
                {comm_analysis_html}
            </div>
            {self._generate_communication_analysis_html(summary, tool_perf, sequence_analysis)}
        </div>

        <!-- Task & Simulation Analysis -->
        <div class="section page-break">
            <h2>📋 Task & Simulation Analysis</h2>
            <div class="plot-container">
                {task_analysis_html}
            </div>
            {self._generate_task_analysis_html(summary, tool_perf, state_analysis)}
        </div>

        <!-- Execution Patterns & Workflow Analysis -->
        <div class="section page-break">
            <h2>🔄 Execution Patterns & Workflow Analysis</h2>
            <div class="plot-container">
                {exec_patterns_html}
            </div>
            {self._generate_execution_patterns_html(summary, tool_perf, sequence_analysis)}
        </div>

        <!-- Tool Performance Deep Dive -->
        <div class="section page-break">
            <h2>⚡ Performance Deep Dive</h2>
            {self._generate_tool_performance_deep_dive_html(tool_perf, failures)}
        </div>

        <!-- Failure Analysis -->
        <div class="section page-break">
            <h2>🔥 Detailed Failure Analysis</h2>
            {self._generate_enhanced_failure_section(failures, summary, tool_perf)}
        </div>

        <div class="footer">
            <p>Report generated by Enhanced Tau2 Analytics Framework</p>
            <p>Interactive visualizations powered by Plotly</p>
        </div>
    </div>
</body>
</html>"""

        # Write the HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _create_performance_issues_plot(self, summary, tool_perf, failures):
        """Create a plot showing performance issues and state-changing vs read-only performance."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Performance by Category", "State-Changing vs Read-Only",
                          "Success Rate vs Calls", "Failure Rate Analysis"),
            specs=[[{"type": "bar"}, {"type": "box"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )

        if not tool_perf.empty:
            # Performance by category
            perf_categories = tool_perf['performance_category'].value_counts()
            fig.add_trace(
                go.Bar(x=perf_categories.index, y=perf_categories.values,
                       marker_color=['#28a745', '#17a2b8', '#ffc107', '#dc3545'],
                       name="Tools by Category"),
                row=1, col=1
            )

            # State-changing vs read-only performance
            state_changing = tool_perf[tool_perf['state_change_rate'] > 0]
            read_only = tool_perf[tool_perf['state_change_rate'] == 0]

            if not state_changing.empty:
                fig.add_trace(
                    go.Box(y=state_changing['success_rate'], name="State-Changing",
                           marker_color="#ff6b6b"),
                    row=1, col=2
                )
            if not read_only.empty:
                fig.add_trace(
                    go.Box(y=read_only['success_rate'], name="Read-Only",
                           marker_color="#4ecdc4"),
                    row=1, col=2
                )

            # Success rate vs calls scatter
            fig.add_trace(
                go.Scatter(
                    x=tool_perf['total_calls'],
                    y=tool_perf['success_rate'],
                    mode='markers+text',
                    marker=dict(
                        size=10,
                        color=tool_perf['success_rate'],
                        colorscale='RdYlGn',
                        showscale=True
                    ),
                    text=tool_perf['tool_name'],
                    textposition="top center",
                    name="Success vs Usage"
                ),
                row=2, col=1
            )

        # Failure rate analysis
        if not failures.empty:
            failure_rates = failures.nlargest(10, 'failure_rate')
            fig.add_trace(
                go.Bar(
                    x=failure_rates['tool_name'],
                    y=failure_rates['failure_rate'],
                    marker_color='#dc3545',
                    name="Failure Rate"
                ),
                row=2, col=2
            )

        fig.update_layout(height=800, showlegend=False, title_text="Performance Issues Analysis")
        return fig

    def _create_communication_analysis_plot(self, summary, tool_perf, sequence_analysis):
        """Create a plot analyzing communication patterns and tool usage."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Tool Usage Distribution", "Transfer vs Communication",
                          "Tool Transition Patterns", "Execution Efficiency"),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "indicator"}]]
        )

        if not tool_perf.empty:
            # Tool usage pie chart
            fig.add_trace(
                go.Pie(labels=tool_perf['tool_name'], values=tool_perf['total_calls'],
                       name="Tool Usage"),
                row=1, col=1
            )

            # Transfer vs communication tools
            transfer_tools = tool_perf[tool_perf['tool_name'].str.contains('transfer|human', case=False, na=False)]
            comm_tools = tool_perf[tool_perf['tool_name'].str.contains('send|message|communicate', case=False, na=False)]

            categories = []
            values = []
            colors = []

            if not transfer_tools.empty:
                categories.extend(transfer_tools['tool_name'].tolist())
                values.extend(transfer_tools['total_calls'].tolist())
                colors.extend(['#007bff'] * len(transfer_tools))

            if not comm_tools.empty:
                categories.extend(comm_tools['tool_name'].tolist())
                values.extend(comm_tools['total_calls'].tolist())
                colors.extend(['#28a745'] * len(comm_tools))

            if categories:
                fig.add_trace(
                    go.Bar(x=categories, y=values, marker_color=colors,
                           name="Communication Tools"),
                    row=1, col=2
                )

        # Tool transition patterns
        if not sequence_analysis.empty:
            top_transitions = sequence_analysis.head(10)
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(top_transitions))),
                    y=top_transitions['count'],
                    mode='markers+lines',
                    marker=dict(size=8, color='#ff6b6b'),
                    name="Transition Frequency"
                ),
                row=2, col=1
            )

        # Execution efficiency gauge
        execution_timespan = summary.get('execution_timespan', 1)
        total_execution_time = summary.get('total_execution_time', 0)
        efficiency = (total_execution_time / execution_timespan * 100) if execution_timespan > 0 else 0

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=efficiency,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Efficiency %"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#4A90E2"},
                    'steps': [
                        {'range': [0, 25], 'color': "#FFF0F0"},
                        {'range': [25, 50], 'color': "#FFF8E7"},
                        {'range': [50, 75], 'color': "#F0FFF4"},
                        {'range': [75, 100], 'color': "#E8F5E8"}
                    ],
                    'threshold': {
                        'line': {'color': "#E74C3C", 'width': 2},
                        'thickness': 0.75,
                        'value': 10
                    }
                }
            ),
            row=2, col=2
        )

        fig.update_layout(height=800, title_text="Communication vs Tool Call Analysis")
        return fig

    def _create_task_analysis_plot(self, summary, tool_perf, state_analysis):
        """Create a plot showing task success correlation with complexity."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=("Task Success Overview", "Complexity vs Success", "State Operations Impact"),
            specs=[[{"type": "indicator"}, {"type": "scatter"}, {"type": "bar"}]]
        )

        # Task success gauge
        task_success_rate = summary.get('task_success_rate', 0)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=task_success_rate * 100,
                title={'text': "Task Success Rate"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#4A90E2"},
                    'steps': [
                        {'range': [0, 40], 'color': "#FFF0F0"},
                        {'range': [40, 70], 'color': "#FFF8E7"},
                        {'range': [70, 100], 'color': "#F0FFF4"}
                    ],
                    'threshold': {
                        'line': {'color': "#E74C3C", 'width': 2},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ),
            row=1, col=1
        )

        # Complexity vs success scatter
        if not tool_perf.empty:
            fig.add_trace(
                go.Scatter(
                    x=tool_perf['total_calls'],
                    y=tool_perf['success_rate'],
                    mode='markers+text',
                    marker=dict(
                        size=tool_perf['total_calls'] / 2,
                        color=tool_perf['state_change_rate'],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="State Change Rate")
                    ),
                    text=tool_perf['tool_name'],
                    name="Tools"
                ),
                row=1, col=2
            )

            # State operations impact
            if not state_analysis.empty:
                state_changing = state_analysis[state_analysis['state_changed'] == True]
                read_only = state_analysis[state_analysis['state_changed'] == False]

                categories = []
                success_rates = []
                colors = []

                if not state_changing.empty:
                    categories.append('State-Changing')
                    success_rates.append(state_changing['success_rate'].mean())
                    colors.append('#ff6b6b')

                if not read_only.empty:
                    categories.append('Read-Only')
                    success_rates.append(read_only['success_rate'].mean())
                    colors.append('#4ecdc4')

                if categories:
                    fig.add_trace(
                        go.Bar(x=categories, y=success_rates, marker_color=colors,
                               name="Success by Type"),
                        row=1, col=3
                    )

        fig.update_layout(height=400, title_text="Task & Simulation Success Analysis")
        return fig

    def _create_execution_patterns_plot(self, summary, tool_perf, sequence_analysis):
        """Create a plot showing execution patterns and workflow analysis."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Tool Call Timeline", "Self-Loop Analysis",
                          "Usage Concentration", "Performance Distribution"),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "histogram"}]]
        )

        if not tool_perf.empty:
            # Tool usage over time (simulated timeline)
            fig.add_trace(
                go.Bar(
                    x=tool_perf['tool_name'],
                    y=tool_perf['total_calls'],
                    marker_color=tool_perf['success_rate'],
                    marker_colorscale='RdYlGn',
                    name="Call Frequency"
                ),
                row=1, col=1
            )

            # Usage concentration
            total_calls = tool_perf['total_calls'].sum()
            most_used_pct = (tool_perf.iloc[0]['total_calls'] / total_calls * 100) if len(tool_perf) > 0 else 0

            fig.add_trace(
                go.Bar(
                    x=['Most Used Tool', 'Other Tools'],
                    y=[most_used_pct, 100 - most_used_pct],
                    marker_color=['#ff6b6b', '#4ecdc4'],
                    name="Usage Distribution"
                ),
                row=2, col=1
            )

            # Performance distribution histogram
            fig.add_trace(
                go.Histogram(
                    x=tool_perf['success_rate'],
                    nbinsx=10,
                    marker_color='#007bff',
                    name="Success Rate Distribution"
                ),
                row=2, col=2
            )

        # Self-loop analysis
        if not sequence_analysis.empty:
            self_loops = sequence_analysis[sequence_analysis['source'] == sequence_analysis['target']]
            other_transitions = sequence_analysis[sequence_analysis['source'] != sequence_analysis['target']]

            if not self_loops.empty or not other_transitions.empty:
                labels = []
                values = []

                if not self_loops.empty:
                    labels.append('Self-Loops')
                    values.append(self_loops['count'].sum())

                if not other_transitions.empty:
                    labels.append('Tool Transitions')
                    values.append(other_transitions['count'].sum())

                if labels:
                    fig.add_trace(
                        go.Pie(labels=labels, values=values, name="Transition Types"),
                        row=1, col=2
                    )

        fig.update_layout(height=800, title_text="Execution Patterns & Workflow Analysis")
        return fig

    def _generate_performance_issues_analysis_html(self, summary, tool_perf, failures):
        """Generate HTML content for performance issues analysis."""
        total_calls = summary.get('total_tool_calls', 0)
        success_rate = summary.get('tool_success_rate', 0)

        html = f"""
        <div class="key-metric">
            Overall Performance Assessment: {success_rate:.1%} ({self._get_performance_category(success_rate)})
        </div>
        """

        if not tool_perf.empty:
            state_changing = tool_perf[tool_perf['state_change_rate'] > 0]
            read_only = tool_perf[tool_perf['state_change_rate'] == 0]

            if not state_changing.empty and not read_only.empty:
                state_avg = state_changing['success_rate'].mean()
                read_avg = read_only['success_rate'].mean()
                performance_drop = read_avg - state_avg

                if performance_drop > 0.2:
                    html += f"""
                    <div class="performance-issue">
                        <strong>Critical Performance Drop:</strong> {performance_drop:.0%}pp drop when state changes are required
                        ({read_avg:.1%} → {state_avg:.1%} success)
                    </div>
                    """
                else:
                    html += f"""
                    <div class="performance-good">
                        <strong>Consistent Performance:</strong> State-changing and read-only operations show similar success rates
                    </div>
                    """

        return html

    def _generate_communication_analysis_html(self, summary, tool_perf, sequence_analysis):
        """Generate HTML content for communication analysis."""
        total_calls = summary.get('total_tool_calls', 0)

        html = ""

        # Transfer analysis
        transfer_tools = tool_perf[tool_perf['tool_name'].str.contains('transfer|human', case=False, na=False)]
        if not transfer_tools.empty:
            transfer_calls = transfer_tools['total_calls'].sum()
            transfer_rate = (transfer_calls / total_calls * 100) if total_calls > 0 else 0
            transfer_success = transfer_tools['success_rate'].mean()

            html += f"""
            <div class="key-metric">
                Transfer to Human: {transfer_calls} calls ({transfer_rate:.1f}% of total) with {transfer_success:.1%} success
            </div>
            """

            if transfer_rate > 20:
                html += f"""
                <div class="performance-issue">
                    <strong>High Transfer Rate:</strong> {transfer_rate:.1f}% transfer rate may indicate agent limitations
                </div>
                """

        # Communication tools
        comm_tools = tool_perf[tool_perf['tool_name'].str.contains('send|message|communicate', case=False, na=False)]
        if not comm_tools.empty:
            comm_calls = comm_tools['total_calls'].sum()
            comm_rate = (comm_calls / total_calls * 100) if total_calls > 0 else 0
            comm_success = comm_tools['success_rate'].mean()

            html += f"""
            <div class="key-metric">
                Communication Tools: {comm_calls} calls ({comm_rate:.1f}% of total) with {comm_success:.1%} success
            </div>
            """

        # Execution efficiency
        execution_timespan = summary.get('execution_timespan', 1)
        total_execution_time = summary.get('total_execution_time', 0)
        efficiency = (total_execution_time / execution_timespan * 100) if execution_timespan > 0 else 0

        html += f"""
        <div class="key-metric">
            Execution Efficiency: {efficiency:.1f}% (time spent in actual tool execution)
        </div>
        """

        if efficiency < 1:
            html += f"""
            <div class="performance-issue">
                <strong>Low Efficiency:</strong> High wait times or communication delays detected
            </div>
            """

        return html

    def _generate_task_analysis_html(self, summary, tool_perf, state_analysis):
        """Generate HTML content for task analysis."""
        total_sims = summary.get('total_simulations', 0)
        task_success_rate = summary.get('task_success_rate', 0)

        html = f"""
        <div class="key-metric">
            Task Completion: {task_success_rate:.1%} success rate across {total_sims} simulations
        </div>
        """

        if task_success_rate >= 0.8:
            html += f"""
            <div class="performance-good">
                <strong>Excellent Task Performance:</strong> System demonstrates high reliability
            </div>
            """
        elif task_success_rate < 0.5:
            html += f"""
            <div class="performance-issue">
                <strong>Critical Task Issues:</strong> Low success rate requires immediate attention
            </div>
            """

        # Complexity analysis
        if not tool_perf.empty and total_sims > 0:
            avg_tools_per_sim = len(tool_perf) / total_sims
            total_tool_calls = summary.get('total_tool_calls', 0)
            avg_calls_per_sim = total_tool_calls / total_sims

            html += f"""
            <div class="key-metric">
                Complexity Metrics: {avg_tools_per_sim:.1f} tools per simulation, {avg_calls_per_sim:.1f} calls per simulation
            </div>
            """

            # State-changing vs read-only impact
            if not state_analysis.empty:
                state_changing = state_analysis[state_analysis['state_changed'] == True]
                if not state_changing.empty:
                    state_calls = state_changing['total_calls'].sum()
                    state_call_rate = (state_calls / total_tool_calls * 100) if total_tool_calls > 0 else 0

                    if task_success_rate < 0.5 and state_call_rate > 20:
                        html += f"""
                        <div class="performance-issue">
                            <strong>State Change Correlation:</strong> High state-change rate ({state_call_rate:.1f}%)
                            with low success suggests action execution issues
                        </div>
                        """

        return html

    def _generate_execution_patterns_html(self, summary, tool_perf, sequence_analysis):
        """Generate HTML content for execution patterns analysis."""
        html = ""

        # Timeline analysis
        execution_timespan = summary.get('execution_timespan', 0)
        total_execution_time = summary.get('total_execution_time', 0)
        total_calls = summary.get('total_tool_calls', 0)

        if execution_timespan > 0:
            call_rate = total_calls / execution_timespan
            html += f"""
            <div class="key-metric">
                Execution Timeline: {execution_timespan:.1f}s total, {call_rate:.2f} calls/second
            </div>
            """

        # Self-loop analysis
        if not sequence_analysis.empty:
            self_loops = sequence_analysis[sequence_analysis['source'] == sequence_analysis['target']]
            if not self_loops.empty:
                total_transitions = sequence_analysis['count'].sum()
                self_loop_count = self_loops['count'].sum()
                self_loop_rate = (self_loop_count / total_transitions * 100) if total_transitions > 0 else 0

                html += f"""
                <div class="key-metric">
                    Self-Loop Pattern: {self_loop_rate:.1f}% of transitions are repeated calls
                </div>
                """

                if self_loop_rate > 30:
                    html += f"""
                    <div class="performance-issue">
                        <strong>High Self-Loop Rate:</strong> May indicate retry logic or iterative processing patterns
                    </div>
                    """

        # Usage concentration
        if not tool_perf.empty:
            total_calls = tool_perf['total_calls'].sum()
            most_used_calls = tool_perf.iloc[0]['total_calls'] if len(tool_perf) > 0 else 0
            concentration = (most_used_calls / total_calls * 100) if total_calls > 0 else 0

            html += f"""
            <div class="key-metric">
                Usage Concentration: {concentration:.1f}% of calls go to most-used tool
            </div>
            """

        return html

    def _generate_tool_performance_deep_dive_html(self, tool_perf, failures):
        """Generate HTML content for tool performance deep dive."""
        if tool_perf.empty:
            return "<p>No tool performance data available.</p>"

        html = """
        <h3>🏆 Performance Tier Analysis</h3>
        """

        # Categorize tools by performance
        excellent_tools = tool_perf[tool_perf['performance_category'] == 'excellent']
        poor_tools = tool_perf[tool_perf['performance_category'] == 'poor']

        if not excellent_tools.empty:
            html += f"""
            <div class="performance-good">
                <h4>Excellent Performance ({len(excellent_tools)} tools)</h4>
                <ul>
            """
            for _, tool in excellent_tools.head(5).iterrows():
                html += f"<li><strong>{tool['tool_name']}</strong>: {tool['success_rate']:.1%} success, {tool['avg_execution_time']*1000:.2f}ms avg time</li>"
            html += "</ul></div>"

        if not poor_tools.empty:
            html += f"""
            <div class="performance-issue">
                <h4>Poor Performance ({len(poor_tools)} tools)</h4>
                <ul>
            """
            for _, tool in poor_tools.head(5).iterrows():
                html += f"<li><strong>{tool['tool_name']}</strong>: {tool['success_rate']:.1%} success, {tool['avg_execution_time']*1000:.2f}ms avg time</li>"
            html += "</ul></div>"

        # High-impact poor performers
        high_usage_poor = poor_tools[poor_tools['total_calls'] >= 5]
        if not high_usage_poor.empty:
            html += """
            <h3>🚨 Critical Performance Issues</h3>
            <div class="performance-issue">
                <h4>High-Usage Poor Performers</h4>
            """
            for _, tool in high_usage_poor.iterrows():
                failed_calls = int(tool['total_calls'] * (1 - tool['success_rate']))
                impact_score = tool['total_calls'] * (1 - tool['success_rate'])
                html += f"""
                <p><strong>{tool['tool_name']}</strong>: {tool['success_rate']:.1%} success rate,
                {int(tool['total_calls'])} total calls, {failed_calls} failed calls,
                Impact Score: {impact_score:.1f}</p>
                """
            html += "</div>"

        return html

    def _get_performance_category(self, success_rate):
        """Get performance category description."""
        if success_rate >= 0.9:
            return "excellent"
        elif success_rate >= 0.7:
            return "good"
        elif success_rate >= 0.5:
            return "concerning"
        else:
            return "critical"

