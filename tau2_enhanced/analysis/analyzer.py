"""
Core analysis tool for processing simplified execution logs from LoggingEnvironment.
"""

import pandas as pd
from typing import Dict, List, Any, Optional


class LogAnalyzer:
    """Analyzes the simple execution logs from LoggingEnvironment."""

    def __init__(self, log_data: List[Dict[str, Any]]):
        """
        Initialize the analyzer with log data.

        Args:
            log_data: A list of log dictionaries, where each dict is an
                      execution log entry from LoggingEnvironment.
        """
        if not log_data:
            self.df = pd.DataFrame()
        else:
            self.df = self._preprocess(log_data)

    def _preprocess(self, log_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Preprocesses the raw log data into a structured DataFrame.

        Args:
            log_data: The raw list of log dictionaries.

        Returns:
            A pandas DataFrame with extracted and cleaned data.
        """
        df = pd.DataFrame(log_data)

        # Extract tool name from tool_call_id
        if 'tool_call_id' in df.columns:
            df['tool_name'] = df['tool_call_id'].apply(
                lambda x: x.split('_')[0] if isinstance(x, str) else 'unknown'
            )
        else:
            df['tool_name'] = 'unknown'

        # Ensure required columns exist
        for col in ['success', 'execution_time', 'error_details']:
            if col not in df.columns:
                df[col] = None

        return df

    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        Calculate high-level summary metrics for the entire execution.

        Returns:
            A dictionary containing summary statistics.
        """
        if self.df.empty:
            return {
                'total_tool_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'success_rate': 0,
                'total_execution_time': 0,
                'average_execution_time': 0,
            }

        total_calls = len(self.df)
        successful_calls = self.df['success'].sum()
        failed_calls = total_calls - successful_calls
        success_rate = successful_calls / total_calls if total_calls > 0 else 0
        total_time = self.df['execution_time'].sum()
        avg_time = self.df['execution_time'].mean()

        return {
            'total_tool_calls': total_calls,
            'successful_calls': int(successful_calls),
            'failed_calls': int(failed_calls),
            'success_rate': success_rate,
            'total_execution_time': total_time,
            'average_execution_time': avg_time,
        }

    def get_tool_performance(self) -> pd.DataFrame:
        """
        Analyze performance metrics for each individual tool.

        Returns:
            A pandas DataFrame with performance metrics per tool, sorted by
            the number of calls.
        """
        if self.df.empty:
            return pd.DataFrame()

        tool_performance = self.df.groupby('tool_name').agg(
            total_calls=('tool_name', 'count'),
            successful_calls=('success', 'sum'),
            avg_execution_time=('execution_time', 'mean'),
            total_execution_time=('execution_time', 'sum')
        ).reset_index()

        tool_performance['failed_calls'] = (
            tool_performance['total_calls'] - tool_performance['successful_calls']
        )
        tool_performance['success_rate'] = (
            tool_performance['successful_calls'] / tool_performance['total_calls']
        )

        return tool_performance.sort_values('total_calls', ascending=False)

    def get_failure_analysis(self) -> pd.DataFrame:
        """
        Analyze the most common failures.

        Returns:
            A pandas DataFrame detailing the most frequent errors.
        """
        if self.df.empty or 'error_details' not in self.df.columns:
            return pd.DataFrame()

        failed_calls = self.df[self.df['success'] == False].copy()
        if failed_calls.empty:
            return pd.DataFrame()

        # Extract error type if available
        failed_calls['error_type'] = failed_calls['error_details'].apply(
            lambda x: type(x).__name__ if x else 'UnknownError'
        )

        error_counts = failed_calls.groupby(['tool_name', 'error_type']).size().reset_index(name='count')

        return error_counts.sort_values('count', ascending=False)

    def identify_bottlenecks(self, time_threshold: float = 1.0) -> pd.DataFrame:
        """
        Identify performance bottlenecks based on execution time.

        Args:
            time_threshold: The execution time in seconds above which a tool
                            call is considered slow.

        Returns:
            A pandas DataFrame of the slowest tool calls.
        """
        if self.df.empty:
            return pd.DataFrame()

        slow_tools = self.df[self.df['execution_time'] > time_threshold]
        return slow_tools.sort_values('execution_time', ascending=False)
