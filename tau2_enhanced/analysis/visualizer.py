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

    def create_summary_dashboard(self) -> go.Figure:
        """
        Create a dashboard summarizing overall tool performance.

        Returns:
            A Plotly Figure object.
        """
        summary = self.analyzer.get_summary_metrics()
        tool_perf = self.analyzer.get_tool_performance()

        fig = make_subplots(
            rows=2,
            cols=2,
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}],
                [{"type": "bar"}, {"type": "bar"}]
            ],
            subplot_titles=("Overall Success Rate", "Avg. Execution Time", "Tool Success Rates", "Tool Execution Times")
        )

        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=summary['success_rate'] * 100,
                title={'text': "Success %"},
                gauge={'axis': {'range': [0, 100]}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Indicator(
                mode="number",
                value=summary['average_execution_time'],
                title={'text': "Avg. Time (s)"},
                number={'suffix': " s"}
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
                    y=tool_perf['avg_execution_time'],
                    name='Avg. Time (s)',
                    marker_color='blue',
                    text=[f"{time:.4f}s" for time in tool_perf['avg_execution_time']],
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
        fig.update_yaxes(title_text="Execution Time (s)", row=2, col=2)

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

        # Create comprehensive failure analysis dashboard
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "table"}]
            ],
            subplot_titles=(
                "Failure Count by Tool",
                "Failure Rate vs Execution Time",
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

        # 2. Failure rate vs execution time scatter (top-right)
        fig.add_trace(
            go.Scatter(
                x=failures['avg_execution_time'],
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
                hovertemplate=(
                    '<b>%{text}</b><br>' +
                    'Failure Rate: %{y:.1%}<br>' +
                    'Avg Execution Time: %{x:.4f}s<br>' +
                    'Error Count: %{marker.color}<extra></extra>'
                )
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
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['<b>Tool</b>', '<b>Error Type</b>', '<b>Count</b>', '<b>Failure Rate</b>', '<b>Avg Time (s)</b>'],
                    fill_color='lightcoral',
                    align='center',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=[
                        table_data['tool_name'],
                        table_data['error_category'],
                        table_data['count'],
                        [f"{rate:.1%}" for rate in table_data['failure_rate']],
                        [f"{time:.4f}" for time in table_data['avg_execution_time']]
                    ],
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
        fig.update_xaxes(title_text="Average Execution Time (s)", row=1, col=2)
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
            yaxis_title="Average Execution Time (s)"
        )
        return fig

    def create_comprehensive_report(self, output_path: str, log_file_name: str = "execution_logs") -> str:
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
        summary_fig = self.create_summary_dashboard()
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
                    <div class="metric-value">{summary.get('total_tool_calls', 0)}</div>
                    <div class="metric-label">Total Tool Calls</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('success_rate', 0):.1%}</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary.get('average_execution_time', 0):.4f}s</div>
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
                            <th>Avg Time (s)</th>
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
                            <th>Avg Time (s)</th>
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

            {self._generate_failure_section(failures, summary)}

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
                    <li>Overall system reliability: <strong>{summary.get('success_rate', 0):.1%}</strong></li>
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
        success_rate = summary.get('success_rate', 1.0)
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
                high_priority.append(f"<strong>High failure rate:</strong> {failure_rate:.1%} of calls are failing. Focus on error handling improvements.")

            # Specific error type recommendations
            error_types = failures['error_category'].unique()
            for error_type in error_types:
                error_count = failures[failures['error_category'] == error_type]['count'].sum()
                affected_tools = failures[failures['error_category'] == error_type]['tool_name'].unique()

                if error_type == 'ValidationError':
                    high_priority.append(f"<strong>Input validation critical:</strong> {error_count} ValidationErrors across {len(affected_tools)} tools: {', '.join(affected_tools[:3])}")
                elif error_type == 'TimeoutError':
                    high_priority.append(f"<strong>Timeout issues:</strong> {error_count} timeouts detected. Consider increasing timeout limits or optimizing performance.")
                elif error_type == 'ConnectionError':
                    high_priority.append(f"<strong>Network reliability:</strong> {error_count} connection errors. Implement robust retry mechanisms.")

        # Analyze tool performance for medium priority recommendations
        if not tool_perf.empty:
            # Poor performing tools
            poor_tools = tool_perf[tool_perf['performance_category'] == 'poor']
            if not poor_tools.empty:
                poor_list = poor_tools['tool_name'].tolist()
                failure_rates = poor_tools['error_rate'].tolist()
                medium_priority.append(f"<strong>Fix failing tools:</strong> {len(poor_list)} tools need attention: " +
                                     ", ".join([f"{tool} ({rate:.1%} failure)" for tool, rate in zip(poor_list[:3], failure_rates[:3])]))

            # Slow tools
            slow_threshold = max(0.1, avg_execution_time * 5)  # Dynamic threshold
            slow_tools = tool_perf[tool_perf['avg_execution_time'] > slow_threshold]
            if not slow_tools.empty:
                slow_list = slow_tools['tool_name'].tolist()
                slow_times = slow_tools['avg_execution_time'].tolist()
                medium_priority.append(f"<strong>Performance optimization needed:</strong> " +
                                     ", ".join([f"{tool} ({time:.3f}s avg)" for tool, time in zip(slow_list[:3], slow_times[:3])]))

            # High-volume tools could benefit from caching
            high_volume = tool_perf[tool_perf['total_calls'] > tool_perf['total_calls'].quantile(0.8)]
            if not high_volume.empty and len(high_volume) > 0:
                cache_candidates = high_volume['tool_name'].tolist()[:3]
                medium_priority.append(f"<strong>Consider caching:</strong> High-usage tools could benefit from result caching: {', '.join(cache_candidates)}")

        # State change analysis recommendations
        if not state_analysis.empty:
            state_changing = state_analysis[state_analysis['state_changed'] == True]
            read_only = state_analysis[state_analysis['state_changed'] == False]

            # Check if state-changing operations have different error patterns than read-only
            if not state_changing.empty and not read_only.empty:
                state_error_rate = state_changing['error_rate'].mean()
                readonly_error_rate = read_only['error_rate'].mean()

                if state_error_rate > readonly_error_rate * 2:  # State operations much more error-prone
                    medium_priority.append(f"<strong>State operation reliability:</strong> State-changing operations have {state_error_rate:.1%} error rate vs {readonly_error_rate:.1%} for read-only operations. Review transaction handling.")

        # Low priority: Best practice recommendations based on data patterns
        if total_calls > 100:  # Only for systems with reasonable usage
            low_priority.append(f"<strong>Monitoring setup:</strong> With {total_calls} tool calls analyzed, implement automated monitoring dashboards.")

        if len(tool_perf) > 5:  # Multi-tool systems
            low_priority.append(f"<strong>Performance baselines:</strong> Establish SLA targets for your {len(tool_perf)} tools based on current performance data.")

        if success_rate > 0.95:  # Well-performing systems
            low_priority.append(f"<strong>Optimization opportunities:</strong> Excellent {success_rate:.1%} success rate! Consider performance profiling for the remaining edge cases.")

        # Tool usage pattern recommendations
        if not tool_perf.empty:
            most_used = tool_perf.iloc[0]
            usage_ratio = most_used['total_calls'] / total_calls
            if usage_ratio > 0.5:  # One tool dominates usage
                low_priority.append(f"<strong>Load distribution:</strong> {most_used['tool_name']} accounts for {usage_ratio:.1%} of calls. Consider load balancing or scaling strategies.")

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
                <td>{row['avg_execution_time']:.4f}</td>
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
                <td>{row['avg_execution_time']:.4f}</td>
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
                        <th>Failure Rate</th>
                        <th>Avg Time (s)</th>
                        <th>First Occurrence</th>
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
                <td>{row['failure_rate']:.1%}</td>
                <td>{row['avg_execution_time']:.4f}</td>
                <td>{str(row['first_occurrence'])[:19]}</td>
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
