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
