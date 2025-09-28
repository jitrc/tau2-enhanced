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
                [{"type": "bar", "colspan": 2}, None]
            ],
            subplot_titles=("Overall Success Rate", "Avg. Execution Time", "Tool Performance")
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
                    marker_color='green'
                ),
                row=2, col=1
            )
            fig.add_trace(
                go.Bar(
                    x=tool_perf['tool_name'],
                    y=tool_perf['avg_execution_time'],
                    name='Avg. Time (s)',
                    marker_color='blue'
                ),
                row=2, col=1
            )

        fig.update_layout(
            title_text="Execution Summary Dashboard",
            height=800
        )
        return fig

    def create_failure_analysis_plot(self) -> go.Figure:
        """
        Create a plot analyzing the root causes of failures.

        Returns:
            A Plotly Figure object.
        """
        failures = self.analyzer.get_failure_analysis()
        if failures.empty:
            return go.Figure().update_layout(title="No Failures Recorded")

        fig = px.treemap(
            failures,
            path=[px.Constant("All Failures"), 'tool_name', 'error_type'],
            values='count',
            title="Failure Analysis by Tool and Error Type"
        )
        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
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
            size_max=60,
            title="Performance Bottlenecks: Calls vs. Avg. Time"
        )
        fig.update_layout(
            xaxis_title="Total Calls",
            yaxis_title="Average Execution Time (s)"
        )
        return fig
