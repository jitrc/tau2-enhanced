"""
Advanced analysis tool for structured execution events from ExecutionLogger.

This analyzer processes rich ToolExecutionEvent objects to provide comprehensive
insights into tau2-bench execution performance and patterns.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from tau2_enhanced.logging import (
    ToolExecutionEvent,
    StateChangeEvent,
    ContextReductionEvent,
    ExecutionEvent,
    LogLevel
)


class LogAnalyzer:
    """
    Advanced analyzer for structured execution events.

    Processes ToolExecutionEvent objects to provide deep insights into
    tool performance, temporal patterns, error analysis, and usage statistics.
    """

    def __init__(self, log_data: Union[List[ToolExecutionEvent], Dict[str, Any]]):
        """
        Initialize the analyzer with structured event data.

        Args:
            log_data: Either:
                - List of ToolExecutionEvent objects
                - Dict with 'execution_events' key containing structured events
        """
        self.tool_events: List[ToolExecutionEvent] = []
        self.raw_log_data = log_data

        if not log_data:
            self.df = pd.DataFrame()
        else:
            self.df = self._preprocess(log_data)

    def _preprocess(self, log_data: Union[List[ToolExecutionEvent], Dict[str, Any]]) -> pd.DataFrame:
        """
        Preprocesses structured event data into an analysis-ready DataFrame.

        Args:
            log_data: Either list of ToolExecutionEvent objects or structured logs dict

        Returns:
            A pandas DataFrame optimized for analysis operations.
        """
        # Detect if this is a https://github.com/jitrc/tau2-bench/tree/xai log format
        if  isinstance(log_data, dict) and 'simulations' in log_data and isinstance(log_data['simulations'], list) and len(log_data['simulations']) > 0 and 'enhanced_logging_enabled' in log_data['simulations'][0]:
            self.tool_events = self._parse_jit_log_data(log_data)

        # Existing logic for enhanced logs
        elif isinstance(log_data, dict) and 'execution_events' in log_data:
            # Extract ToolExecutionEvents from structured logs
            self.tool_events = []
            for event_data in log_data['execution_events']:
                if isinstance(event_data, dict) and event_data.get('event_type') == 'ToolExecutionEvent':
                    # Convert dict back to ToolExecutionEvent if needed
                    from tau2_enhanced.logging.events import event_from_dict
                    event = event_from_dict(event_data)
                    if isinstance(event, ToolExecutionEvent):
                        self.tool_events.append(event)
                elif isinstance(event_data, ToolExecutionEvent):
                    self.tool_events.append(event_data)
        elif isinstance(log_data, list):
            # List of ToolExecutionEvent objects
            self.tool_events = [e for e in log_data if isinstance(e, ToolExecutionEvent)]

        if not self.tool_events:
            return pd.DataFrame()

        # Convert events to structured DataFrame
        event_dicts = [event.to_dict() if not isinstance(event, dict) else event for event in self.tool_events]
        
        # Ensure execution_time is correctly populated
        for event in event_dicts:
            if 'execution_time_ms' in event:
                event['execution_time'] = event['execution_time_ms'] / 1000.0
        
        df = pd.DataFrame(event_dicts)

        # Handle datetime conversion
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')

        # Ensure tool_name is properly extracted
        if 'tool_name' not in df.columns and 'tool_call_id' in df.columns:
            df['tool_name'] = df['tool_call_id'].apply(
                lambda x: '_'.join(x.split('_')[:-1]) if isinstance(x, str) and x.split('_')[-1].isdigit() else x
            )

        # Standardize error information
        if 'error_message' in df.columns:
            df['error_details'] = df['error_message']  # Use error_message as primary error field

        # Ensure execution_time is numeric
        if 'execution_time' in df.columns:
            df['execution_time'] = pd.to_numeric(df['execution_time'], errors='coerce').fillna(0)

        return df

    def _parse_jit_log_data(self, log_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses the log data from tau2-bench-jit format.
        """
        tool_events = []
        sim_iterator = log_data.get('simulations', [])
        if isinstance(sim_iterator, dict):
            sim_iterator = sim_iterator.values()

        for sim in sim_iterator:
            if 'execution_logs' in sim and sim['execution_logs'] is not None:
                for log in sim['execution_logs']:
                    tool_args = log.get('arguments', {})
                    if not isinstance(tool_args, dict):
                        tool_args = {}
                    result = log.get('result_preview')

                    # Argument analysis
                    args_count = len(tool_args)
                    args_size_bytes = len(str(tool_args))
                    has_large_args = args_size_bytes > 1024
                    args_types = {k: type(v).__name__ for k, v in tool_args.items()}
                    
                    complexity_factors = [
                        len(tool_args) * 0.1,
                        sum(1 for v in tool_args.values() if isinstance(v, (dict, list))) * 0.2,
                        sum(1 for v in tool_args.values() if isinstance(v, str) and len(v) > 100) * 0.15,
                        (args_size_bytes / 1024) * 0.1
                    ]
                    args_complexity_score = min(sum(complexity_factors), 1.0)

                    sensitive_indicators = ['password', 'key', 'secret', 'token', 'auth', 'credential', 'ssn', 'credit']
                    sensitive_args_detected = any(any(indicator in str(k).lower() for indicator in sensitive_indicators) for k in tool_args.keys())

                    # Result analysis
                    result_type = type(result).__name__ if result is not None else None
                    result_size = len(str(result)) if result is not None else 0
                    
                    # Timestamp conversion
                    timestamp = 0.0
                    if log.get('pre_call_timestamp'):
                        try:
                            ts_str = log.get('pre_call_timestamp')
                            if isinstance(ts_str, str):
                                if ts_str.endswith('Z'):
                                    ts_str = ts_str[:-1] + '+00:00'
                                timestamp = datetime.fromisoformat(ts_str).timestamp()
                        except Exception:
                            timestamp = 0.0
                    elif log.get('timestamp'):
                        timestamp = log.get('timestamp', 0.0)

                    # Handle execution time from different formats
                    execution_time = 0.0
                    if 'execution_time_ms' in log:
                        execution_time = log.get('execution_time_ms', 0) / 1000.0
                    elif 'execution_time' in log:
                        execution_time = log.get('execution_time', 0)

                    # Handle error messages from different formats
                    error_message = log.get('error_details')
                    if error_message is None:
                        error_message = log.get('error_message')

                    # Heuristic to infer state_changed for jit logs
                    state_changed = log.get('state_changed', False)
                    if not state_changed:
                        tool_name = log.get('tool_name', '')
                        if any(keyword in tool_name for keyword in ['update', 'cancel', 'book', 'send', 'create', 'delete', 'add', 'remove']):
                            state_changed = True

                    # Map jit log fields to ToolExecutionEvent fields
                    event_dict = {
                        'tool_name': log.get('tool_name'),
                        'tool_call_id': log.get('tool_call_id'),
                        'tool_args': tool_args,
                        'timestamp': timestamp,
                        'execution_time': execution_time,
                        'success': log.get('success'),
                        'error_message': error_message,
                        'requestor': log.get('requestor'),
                        'result_preview': result,
                        'state_changed': state_changed,
                        'level': LogLevel.INFO if log.get('success') else LogLevel.ERROR,
                        'source': f"tool:{log.get('tool_name')}",
                        'message': f"Tool {log.get('tool_name')} {'succeeded' if log.get('success') else 'failed'}",
                        'metadata': {},
                        'error_type': log.get('error_type'),
                        'result_size': result_size,
                        'validation_errors': log.get('validation_errors', []),
                        'args_count': args_count,
                        'args_size_bytes': args_size_bytes,
                        'args_types': args_types,
                        'args_complexity_score': args_complexity_score,
                        'has_file_args': False, 
                        'has_large_args': has_large_args,
                        'sensitive_args_detected': sensitive_args_detected,
                        'required_args_provided': [],
                        'optional_args_provided': [],
                        'missing_args': [],
                        'unexpected_args': [],
                        'result_type': result_type,
                        'result_complexity_score': None,
                        'result_contains_errors': False,
                        'result_truncated': False,
                        'has_result': result is not None,
                    }
                    tool_events.append(event_dict)
        return tool_events

    def _calculate_action_check_success_rates(self) -> Dict[str, Any]:
        """
        Calculate tool success rates based on action check results from simulations.

        Returns:
            Dictionary with action check success metrics
        """
        if not hasattr(self, 'raw_log_data') or not self.raw_log_data:
            return {'has_action_checks': False}

        simulations = self.raw_log_data.get('simulations', [])
        if not simulations:
            return {'has_action_checks': False}

        # Collect all action checks across simulations
        all_actions = []
        sim_iterator = simulations.values() if isinstance(simulations, dict) else simulations

        for sim in sim_iterator:
            reward_info = sim.get('reward_info', {})
            action_checks = reward_info.get('action_checks')

            if action_checks and isinstance(action_checks, list):
                for check in action_checks:
                    if isinstance(check, dict):
                        action = check.get('action', {})
                        all_actions.append({
                            'tool_name': action.get('name'),
                            'action_match': check.get('action_match', False),
                            'action_reward': check.get('action_reward', 0.0),
                            'simulation_id': sim.get('id', 'unknown')
                        })

        if not all_actions:
            return {'has_action_checks': False}

        # Calculate overall success metrics based on action checks
        total_actions = len(all_actions)
        successful_actions = sum(1 for action in all_actions if action['action_match'])
        failed_actions = total_actions - successful_actions

        action_success_rate = successful_actions / total_actions if total_actions > 0 else 0

        # Calculate per-tool success rates based on action checks
        tool_action_stats = {}
        for action in all_actions:
            tool_name = action['tool_name']
            if tool_name not in tool_action_stats:
                tool_action_stats[tool_name] = {'total': 0, 'successful': 0}

            tool_action_stats[tool_name]['total'] += 1
            if action['action_match']:
                tool_action_stats[tool_name]['successful'] += 1

        # Calculate success rates per tool
        for tool_name in tool_action_stats:
            stats = tool_action_stats[tool_name]
            stats['success_rate'] = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            stats['failed'] = stats['total'] - stats['successful']

        return {
            'has_action_checks': True,
            'total_actions_checked': total_actions,
            'successful_actions': successful_actions,
            'failed_actions': failed_actions,
            'action_check_success_rate': action_success_rate,
            'tool_action_stats': tool_action_stats
        }

    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        Calculate enhanced high-level summary metrics for the entire execution.

        Returns:
            A dictionary containing comprehensive summary statistics.
        """
        if self.df.empty:
            return {
                'total_tool_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'tool_success_rate': 0,
                'total_execution_time': 0,
                'average_execution_time': 0,
                'median_execution_time': 0,
                'state_changing_calls': 0,
                'read_only_calls': 0,
                'tool_error_rate': 0,
                'most_common_tool': None,
                'slowest_tool_avg': None,
                'fastest_tool_avg': None,
                'execution_timespan': None,
                'tools_used': 0,
                'total_simulations': 0,
                'successful_simulations': 0,
                'task_success_rate': 0,
            }

        # --- Task-level metrics ---
        simulations = self.raw_log_data.get('simulations', [])
        total_simulations = len(simulations)
        successful_simulations = 0
        if simulations:
            # Handle both list and dict of simulations
            sim_iterator = simulations.values() if isinstance(simulations, dict) else simulations
            for sim in sim_iterator:
                reward_info = sim.get('reward_info')
                if reward_info and reward_info.get('reward', 0) > 0:
                    successful_simulations += 1
        task_success_rate = successful_simulations / total_simulations if total_simulations > 0 else 0

        # --- Tool-level metrics ---
        total_calls = len(self.df)

        # Try to use action check success rates first (more accurate for tool effectiveness)
        action_check_metrics = self._calculate_action_check_success_rates()

        if action_check_metrics['has_action_checks']:
            # Use action check success rates as the primary tool success metric
            successful_calls = action_check_metrics['successful_actions']
            failed_calls = action_check_metrics['failed_actions']
            tool_success_rate = action_check_metrics['action_check_success_rate']
            tool_error_rate = 1 - tool_success_rate
            success_metric_source = 'action_checks'
        else:
            # Fallback to execution success (API call didn't throw exception)
            successful_calls = self.df['success'].sum()
            failed_calls = total_calls - successful_calls
            tool_success_rate = successful_calls / total_calls if total_calls > 0 else 0
            tool_error_rate = failed_calls / total_calls if total_calls > 0 else 0
            success_metric_source = 'execution_success'

        # Time-based metrics
        total_time = self.df['execution_time'].sum()
        avg_time = self.df['execution_time'].mean()
        median_time = self.df['execution_time'].median()

        # State change analysis
        state_changing = self.df['state_changed'].sum()
        read_only = total_calls - state_changing

        # Tool usage analysis
        tool_counts = self.df['tool_name'].value_counts()
        most_common_tool = tool_counts.index[0] if not tool_counts.empty else None
        tools_used = len(tool_counts)

        # Tool performance analysis
        tool_times = self.df.groupby('tool_name')['execution_time'].mean()
        slowest_tool_avg = tool_times.idxmax() if not tool_times.empty else None
        fastest_tool_avg = tool_times.idxmin() if not tool_times.empty else None

        # Time span analysis
        execution_timespan = None
        if 'datetime' in self.df.columns and self.df['datetime'].notna().any():
            time_range = self.df['datetime'].max() - self.df['datetime'].min()
            execution_timespan = time_range.total_seconds()

        return {
            'total_simulations': total_simulations,
            'successful_simulations': successful_simulations,
            'task_success_rate': task_success_rate,
            'total_tool_calls': total_calls,
            'successful_calls': int(successful_calls),
            'failed_calls': int(failed_calls),
            'tool_success_rate': tool_success_rate,
            'tool_error_rate': tool_error_rate,
            'total_execution_time': total_time,
            'average_execution_time': avg_time,
            'median_execution_time': median_time,
            'state_changing_calls': int(state_changing),
            'read_only_calls': int(read_only),
            'most_common_tool': most_common_tool,
            'slowest_tool_avg': slowest_tool_avg,
            'fastest_tool_avg': fastest_tool_avg,
            'execution_timespan': execution_timespan,
            'tools_used': tools_used,
            'success_metric_source': success_metric_source
        }

    def get_tool_performance(self) -> pd.DataFrame:
        """
        Analyze enhanced performance metrics for each individual tool.

        Returns:
            A pandas DataFrame with comprehensive performance metrics per tool,
            sorted by the number of calls.
        """
        if self.df.empty:
            return pd.DataFrame()

        # Enhanced aggregation with more metrics
        tool_performance = self.df.groupby('tool_name').agg(
            total_calls=('tool_name', 'count'),
            successful_calls=('success', 'sum'),
            avg_execution_time=('execution_time', 'mean'),
            median_execution_time=('execution_time', 'median'),
            min_execution_time=('execution_time', 'min'),
            max_execution_time=('execution_time', 'max'),
            total_execution_time=('execution_time', 'sum'),
            state_changing_calls=('state_changed', 'sum'),
            avg_result_size=('result_size', lambda x: x.dropna().mean() if x.dropna().any() else 0)
        ).reset_index()

        # Try to use action check success rates for per-tool metrics
        action_check_metrics = self._calculate_action_check_success_rates()

        if action_check_metrics['has_action_checks']:
            # Override success rates with action check results
            tool_action_stats = action_check_metrics['tool_action_stats']

            for idx, row in tool_performance.iterrows():
                tool_name = row['tool_name']
                if tool_name in tool_action_stats:
                    stats = tool_action_stats[tool_name]
                    tool_performance.at[idx, 'successful_calls'] = stats['successful']
                    tool_performance.at[idx, 'failed_calls'] = stats['failed']
                else:
                    # No action checks for this tool, keep execution success
                    tool_performance.at[idx, 'failed_calls'] = (
                        tool_performance.at[idx, 'total_calls'] - tool_performance.at[idx, 'successful_calls']
                    )

            success_metric_source = 'action_checks'
        else:
            # Calculate derived metrics using execution success
            tool_performance['failed_calls'] = (
                tool_performance['total_calls'] - tool_performance['successful_calls']
            )
            success_metric_source = 'execution_success'

        # Calculate success and error rates
        tool_performance['success_rate'] = (
            tool_performance['successful_calls'] / tool_performance['total_calls']
        )
        tool_performance['error_rate'] = (
            tool_performance['failed_calls'] / tool_performance['total_calls']
        )
        tool_performance['state_change_rate'] = (
            tool_performance['state_changing_calls'] / tool_performance['total_calls']
        )

        # Performance category classification
        def classify_performance(row):
            if row['success_rate'] >= 0.95 and row['avg_execution_time'] <= 1.0:
                return 'excellent'
            elif row['success_rate'] >= 0.90 and row['avg_execution_time'] <= 2.0:
                return 'good'
            elif row['success_rate'] >= 0.75:
                return 'fair'
            else:
                return 'poor'

        tool_performance['performance_category'] = tool_performance.apply(classify_performance, axis=1)

        return tool_performance.sort_values('total_calls', ascending=False)

    def get_failure_analysis(self) -> pd.DataFrame:
        """
        Analyze the most common failures with enhanced error categorization.
        Uses action check failures when available for more accurate failure analysis.

        Returns:
            A pandas DataFrame detailing comprehensive error analysis.
        """
        if self.df.empty:
            return pd.DataFrame()

        # Try to use action check failures first (more accurate)
        action_check_metrics = self._calculate_action_check_success_rates()

        if action_check_metrics['has_action_checks']:
            # Build failure analysis from action check data
            failed_actions = []

            # Extract failed actions from simulations
            simulations = self.raw_log_data.get('simulations', [])
            sim_iterator = simulations.values() if isinstance(simulations, dict) else simulations

            for sim in sim_iterator:
                reward_info = sim.get('reward_info', {})
                action_checks = reward_info.get('action_checks')

                if action_checks and isinstance(action_checks, list):
                    for check in action_checks:
                        if isinstance(check, dict) and not check.get('action_match', False):
                            action = check.get('action', {})
                            failed_actions.append({
                                'tool_name': action.get('name', 'unknown'),
                                'error_category': 'ActionCheckFailure',
                                'simulation_id': sim.get('id', 'unknown'),
                                'task_id': sim.get('task_id', 'unknown'),
                                'action_reward': check.get('action_reward', 0.0),
                                'arguments': str(action.get('arguments', {}))[:100] + '...' if len(str(action.get('arguments', {}))) > 100 else str(action.get('arguments', {}))
                            })

            if failed_actions:
                # Create DataFrame from failed actions
                failed_df = pd.DataFrame(failed_actions)

                # Aggregate failure analysis
                error_analysis = failed_df.groupby(['tool_name', 'error_category']).agg(
                    count=('tool_name', 'count'),
                    simulations_affected=('simulation_id', 'nunique'),
                    avg_action_reward=('action_reward', 'mean')
                ).reset_index()

                # Add failure rate for each tool
                tool_action_stats = action_check_metrics['tool_action_stats']
                error_analysis['failure_rate'] = error_analysis.apply(
                    lambda row: row['count'] / tool_action_stats.get(row['tool_name'], {}).get('total', 1), axis=1
                )

                # Add example failed arguments
                error_analysis['example_args'] = error_analysis.apply(
                    lambda row: failed_df[(failed_df['tool_name'] == row['tool_name']) &
                                        (failed_df['error_category'] == row['error_category'])]['arguments'].iloc[0], axis=1
                )

                return error_analysis.sort_values('count', ascending=False)
            else:
                # No action check failures found
                return pd.DataFrame()

        else:
            # Fallback to execution failures
            failed_calls = self.df[self.df['success'] == False].copy()
            if failed_calls.empty:
                return pd.DataFrame()

            # Enhanced error type extraction
            def extract_error_type(row):
                if pd.notna(row.get('error_type')):
                    return row['error_type']
                elif pd.notna(row.get('error_details')):
                    error_detail = str(row['error_details'])
                    if 'timeout' in error_detail.lower():
                        return 'TimeoutError'
                    elif 'connection' in error_detail.lower():
                        return 'ConnectionError'
                    elif 'permission' in error_detail.lower() or 'forbidden' in error_detail.lower():
                        return 'PermissionError'
                    elif 'not found' in error_detail.lower():
                        return 'NotFoundError'
                    elif 'validation' in error_detail.lower():
                        return 'ValidationError'
                    else:
                        return 'UnknownError'
                else:
                    return 'UnknownError'

            failed_calls['error_category'] = failed_calls.apply(extract_error_type, axis=1)

            # Comprehensive error analysis
            error_analysis = failed_calls.groupby(['tool_name', 'error_category']).agg(
                count=('tool_name', 'count'),
                avg_execution_time=('execution_time', 'mean'),
                first_occurrence=('datetime', 'min') if 'datetime' in failed_calls.columns else ('timestamp', 'min'),
                last_occurrence=('datetime', 'max') if 'datetime' in failed_calls.columns else ('timestamp', 'max')
            ).reset_index()

            # Add failure rate for each tool-error combination
            total_calls_per_tool = self.df.groupby('tool_name').size()
            error_analysis['failure_rate'] = error_analysis.apply(
                lambda row: row['count'] / total_calls_per_tool.get(row['tool_name'], 1), axis=1
            )

            return error_analysis.sort_values('count', ascending=False)

    def get_state_change_analysis(self) -> pd.DataFrame:
        """
        Analyzes performance based on whether a tool call changed the state,
        with detailed breakdown by function names.

        Returns:
            A pandas DataFrame summarizing metrics for state-changing vs.
            non-state-changing calls, including per-tool breakdown.
        """
        if self.df.empty or 'state_changed' not in self.df.columns:
            return pd.DataFrame()

        # Enhanced analysis with tool-level breakdown
        state_analysis = self.df.groupby(['state_changed', 'tool_name']).agg(
            total_calls=('state_changed', 'count'),
            successful_calls=('success', 'sum'),
            avg_execution_time=('execution_time', 'mean'),
            min_execution_time=('execution_time', 'min'),
            max_execution_time=('execution_time', 'max')
        ).reset_index()

        # Calculate derived metrics
        state_analysis['failed_calls'] = (
            state_analysis['total_calls'] - state_analysis['successful_calls']
        )
        state_analysis['success_rate'] = (
            state_analysis['successful_calls'] / state_analysis['total_calls']
        )
        state_analysis['error_rate'] = (
            state_analysis['failed_calls'] / state_analysis['total_calls']
        )

        # Add category labels
        state_analysis['category'] = state_analysis['state_changed'].apply(
            lambda x: 'State-Changing' if x else 'Read-Only'
        )

        # Add performance classification
        def classify_tool_performance(row):
            if row['success_rate'] >= 0.95 and row['avg_execution_time'] <= 0.1:
                return 'excellent'
            elif row['success_rate'] >= 0.90 and row['avg_execution_time'] <= 0.5:
                return 'good'
            elif row['success_rate'] >= 0.75:
                return 'fair'
            else:
                return 'poor'

        state_analysis['performance_rating'] = state_analysis.apply(classify_tool_performance, axis=1)

        # Sort by category (state-changing first) then by total calls
        state_analysis = state_analysis.sort_values(['state_changed', 'total_calls'], ascending=[False, False])

        return state_analysis

    def get_tool_sequence_analysis(self) -> pd.DataFrame:
        """
        Analyzes the sequence of tool calls to find common transitions.

        Returns:
            A pandas DataFrame showing the frequency of tool transitions (bigrams).
        """
        if self.df.empty or len(self.df) < 2:
            return pd.DataFrame()

        tool_sequence = self.df['tool_name'].tolist()
        
        # Create bigrams (pairs of consecutive tool calls)
        bigrams = list(zip(tool_sequence[:-1], tool_sequence[1:]))
        
        if not bigrams:
            return pd.DataFrame()

        # Count the frequency of each bigram
        bigram_counts = pd.Series(bigrams).value_counts().reset_index()
        bigram_counts.columns = ['transition', 'count']
        
        # Split the transition tuple into source and target columns
        bigram_counts[['source', 'target']] = pd.DataFrame(
            bigram_counts['transition'].tolist(), index=bigram_counts.index
        )
        
        return bigram_counts[['source', 'target', 'count']].sort_values(
            'count', ascending=False
        )

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

    def get_temporal_analysis(self) -> Dict[str, Any]:
        """
        Analyze temporal patterns in tool execution.

        Returns:
            Dictionary containing temporal analysis results.
        """
        if self.df.empty or 'datetime' not in self.df.columns:
            return {'error': 'No temporal data available'}

        df_with_time = self.df[self.df['datetime'].notna()].copy()
        if df_with_time.empty:
            return {'error': 'No valid timestamps found'}

        # Extract temporal features
        df_with_time['hour'] = df_with_time['datetime'].dt.hour
        df_with_time['minute'] = df_with_time['datetime'].dt.minute
        df_with_time['second'] = df_with_time['datetime'].dt.second

        # Time-based aggregations
        hourly_activity = df_with_time.groupby('hour').agg(
            call_count=('tool_name', 'count'),
            avg_execution_time=('execution_time', 'mean'),
            success_rate=('success', 'mean'),
            state_change_rate=('state_changed', 'mean')
        )

        # Find peak and quiet periods
        peak_hour = hourly_activity['call_count'].idxmax()
        quiet_hour = hourly_activity['call_count'].idxmin()

        # Calculate execution velocity (calls per minute)
        time_span = df_with_time['datetime'].max() - df_with_time['datetime'].min()
        total_minutes = time_span.total_seconds() / 60 if time_span.total_seconds() > 0 else 1
        velocity = len(df_with_time) / total_minutes

        return {
            'execution_velocity_per_minute': velocity,
            'peak_activity_hour': peak_hour,
            'quiet_activity_hour': quiet_hour,
            'hourly_patterns': hourly_activity.to_dict(),
            'time_span_minutes': total_minutes,
            'first_call': df_with_time['datetime'].min().isoformat(),
            'last_call': df_with_time['datetime'].max().isoformat()
        }

    def get_performance_trends(self) -> Dict[str, Any]:
        """
        Analyze performance trends over time.

        Returns:
            Dictionary containing trend analysis.
        """
        if self.df.empty or 'datetime' not in self.df.columns:
            return {'error': 'No temporal data available for trend analysis'}

        df_with_time = self.df[self.df['datetime'].notna()].copy()
        if len(df_with_time) < 10:
            return {'error': 'Insufficient data for trend analysis'}

        # Sort by time and create time windows
        df_sorted = df_with_time.sort_values('datetime')

        # Split into time buckets (10 equal buckets)
        df_sorted['time_bucket'] = pd.cut(range(len(df_sorted)), bins=10, labels=False)

        # Analyze trends across buckets
        bucket_trends = df_sorted.groupby('time_bucket').agg(
            success_rate=('success', 'mean'),
            avg_execution_time=('execution_time', 'mean'),
            call_count=('tool_name', 'count'),
            state_change_rate=('state_changed', 'mean')
        )

        # Calculate trend directions
        success_trend = 'improving' if bucket_trends['success_rate'].iloc[-1] > bucket_trends['success_rate'].iloc[0] else 'degrading'
        speed_trend = 'improving' if bucket_trends['avg_execution_time'].iloc[-1] < bucket_trends['avg_execution_time'].iloc[0] else 'degrading'

        return {
            'success_rate_trend': success_trend,
            'execution_speed_trend': speed_trend,
            'bucket_analysis': bucket_trends.to_dict(),
            'trend_confidence': 'high' if len(df_sorted) > 50 else 'low'
        }

    def get_tool_usage_patterns(self) -> Dict[str, Any]:
        """
        Analyze tool usage patterns and relationships.

        Returns:
            Dictionary containing usage pattern analysis.
        """
        if self.df.empty:
            return {'error': 'No data available'}

        # Tool frequency analysis
        tool_counts = self.df['tool_name'].value_counts()
        total_calls = len(self.df)

        # Usage distribution analysis
        usage_stats = {
            'total_unique_tools': len(tool_counts),
            'most_used_tool': {
                'name': tool_counts.index[0],
                'calls': tool_counts.iloc[0],
                'percentage': tool_counts.iloc[0] / total_calls * 100
            },
            'least_used_tool': {
                'name': tool_counts.index[-1],
                'calls': tool_counts.iloc[-1],
                'percentage': tool_counts.iloc[-1] / total_calls * 100
            },
            'tool_usage_distribution': tool_counts.to_dict()
        }

        # Tool diversity analysis
        # Calculate Shannon diversity index for tool usage
        proportions = tool_counts / total_calls
        diversity_index = -sum(p * np.log(p) for p in proportions if p > 0)

        usage_stats['diversity_index'] = diversity_index
        usage_stats['usage_concentration'] = 'high' if tool_counts.iloc[0] / total_calls > 0.5 else 'distributed'

        return usage_stats

    def get_error_pattern_analysis(self) -> Dict[str, Any]:
        """
        Analyze detailed error patterns and correlations.

        Returns:
            Dictionary containing error pattern analysis.
        """
        if self.df.empty:
            return {'error': 'No data available'}

        failed_calls = self.df[self.df['success'] == False]
        if failed_calls.empty:
            return {'no_errors': True, 'total_calls': len(self.df)}

        # Error timing analysis
        error_analysis = {
            'total_errors': len(failed_calls),
            'error_rate': len(failed_calls) / len(self.df),
            'tools_with_errors': failed_calls['tool_name'].nunique(),
            'error_types': {}
        }

        # Error type analysis
        if 'error_type' in failed_calls.columns:
            error_types = failed_calls['error_type'].value_counts()
            error_analysis['error_types'] = error_types.to_dict()
            error_analysis['most_common_error'] = error_types.index[0] if not error_types.empty else None

        # Error correlation with execution time
        if 'execution_time' in failed_calls.columns:
            avg_error_time = failed_calls['execution_time'].mean()
            avg_success_time = self.df[self.df['success'] == True]['execution_time'].mean()

            error_analysis['avg_error_execution_time'] = avg_error_time
            error_analysis['avg_success_execution_time'] = avg_success_time
            error_analysis['error_time_correlation'] = 'longer' if avg_error_time > avg_success_time else 'shorter'

        # Tool error patterns
        tool_error_rates = failed_calls.groupby('tool_name').size() / self.df.groupby('tool_name').size()
        error_analysis['tools_by_error_rate'] = tool_error_rates.sort_values(ascending=False).to_dict()

        return error_analysis

    def get_requestor_analysis(self) -> Dict[str, Any]:
        """
        Analyze performance by requestor (agent vs user).

        Returns:
            Dictionary containing requestor-based analysis.
        """
        if self.df.empty or 'requestor' not in self.df.columns:
            return {'error': 'No requestor data available'}

        requestor_analysis = {}

        for requestor in self.df['requestor'].unique():
            requestor_data = self.df[self.df['requestor'] == requestor]

            requestor_analysis[requestor] = {
                'total_calls': len(requestor_data),
                'success_rate': requestor_data['success'].mean(),
                'avg_execution_time': requestor_data['execution_time'].mean(),
                'state_change_rate': requestor_data['state_changed'].mean(),
                'most_used_tools': requestor_data['tool_name'].value_counts().head(3).to_dict(),
                'error_rate': (requestor_data['success'] == False).mean()
            }

        # Overall comparison
        comparison = {
            'requestor_breakdown': requestor_analysis,
            'total_requestors': len(requestor_analysis)
        }

        # Performance comparison if both agent and assistant present
        if 'agent' in requestor_analysis and 'assistant' in requestor_analysis:
            agent_success = requestor_analysis['agent']['success_rate']
            assistant_success = requestor_analysis['assistant']['success_rate']

            comparison['performance_leader'] = 'agent' if agent_success > assistant_success else 'assistant'
            comparison['success_rate_difference'] = abs(agent_success - assistant_success)

        return comparison

    def get_advanced_statistics(self) -> Dict[str, Any]:
        """
        Calculate advanced statistical measures.

        Returns:
            Dictionary containing advanced statistical analysis.
        """
        if self.df.empty:
            return {'error': 'No data available'}

        stats = {}

        # Execution time statistics
        if 'execution_time' in self.df.columns:
            exec_times = self.df['execution_time'].dropna()
            if not exec_times.empty:
                stats['execution_time_stats'] = {
                    'mean': exec_times.mean(),
                    'median': exec_times.median(),
                    'std': exec_times.std(),
                    'min': exec_times.min(),
                    'max': exec_times.max(),
                    'p25': exec_times.quantile(0.25),
                    'p75': exec_times.quantile(0.75),
                    'p95': exec_times.quantile(0.95),
                    'p99': exec_times.quantile(0.99)
                }

        # Success rate confidence intervals (using binomial distribution)
        if 'success' in self.df.columns:
            successes = self.df['success'].sum()
            total = len(self.df)
            success_rate = successes / total if total > 0 else 0

            # Simple 95% confidence interval for proportion
            margin_of_error = 1.96 * np.sqrt(success_rate * (1 - success_rate) / total) if total > 0 else 0

            stats['success_rate_confidence'] = {
                'rate': success_rate,
                'lower_bound': max(0, success_rate - margin_of_error),
                'upper_bound': min(1, success_rate + margin_of_error),
                'sample_size': total
            }

        # Tool call distribution analysis
        tool_counts = self.df['tool_name'].value_counts()
        if not tool_counts.empty:
            stats['tool_distribution'] = {
                'entropy': -sum((count / len(self.df)) * np.log(count / len(self.df))
                              for count in tool_counts if count > 0),
                'gini_coefficient': self._calculate_gini(tool_counts.values),
                'concentration_ratio': tool_counts.iloc[0] / tool_counts.sum()  # Top tool concentration
            }

        return stats

    def _calculate_gini(self, values):
        """Calculate Gini coefficient for inequality measurement."""
        if len(values) == 0:
            return 0

        # Sort values
        sorted_values = sorted(values)
        n = len(sorted_values)

        # Calculate Gini coefficient
        numerator = sum((2 * i - n - 1) * value for i, value in enumerate(sorted_values, 1))
        denominator = n * sum(sorted_values)

        return numerator / denominator if denominator > 0 else 0

    def get_argument_analysis(self) -> Dict[str, Any]:
        """
        Analyze function call arguments patterns and characteristics.

        Returns:
            Dictionary containing comprehensive argument analysis
        """
        if self.df.empty:
            return {'error': 'No data available'}

        analysis = {
            'argument_statistics': {},
            'complexity_analysis': {},
            'type_analysis': {},
            'size_analysis': {},
            'security_analysis': {},
            'usage_patterns': {}
        }

        # Basic argument statistics
        total_calls = len(self.df)
        calls_with_args = len(self.df[self.df['args_count'] > 0])

        analysis['argument_statistics'] = {
            'total_calls': total_calls,
            'calls_with_arguments': calls_with_args,
            'calls_without_arguments': total_calls - calls_with_args,
            'avg_args_per_call': self.df['args_count'].mean(),
            'max_args_in_call': self.df['args_count'].max(),
            'min_args_in_call': self.df['args_count'].min()
        }

        # Complexity analysis
        if 'args_complexity_score' in self.df.columns:
            complexity_data = self.df['args_complexity_score'].dropna()
            if not complexity_data.empty:
                analysis['complexity_analysis'] = {
                    'avg_complexity': complexity_data.mean(),
                    'max_complexity': complexity_data.max(),
                    'high_complexity_calls': len(complexity_data[complexity_data > 0.7]),
                    'low_complexity_calls': len(complexity_data[complexity_data < 0.3]),
                    'complexity_distribution': {
                        'low (0-0.3)': len(complexity_data[complexity_data <= 0.3]),
                        'medium (0.3-0.7)': len(complexity_data[(complexity_data > 0.3) & (complexity_data <= 0.7)]),
                        'high (0.7-1.0)': len(complexity_data[complexity_data > 0.7])
                    }
                }

        # Argument type analysis
        if 'args_types' in self.df.columns:
            all_types = []
            for types_dict in self.df['args_types'].dropna():
                if isinstance(types_dict, dict):
                    all_types.extend(types_dict.values())

            if all_types:
                type_counts = pd.Series(all_types).value_counts()
                analysis['type_analysis'] = {
                    'most_common_types': type_counts.head(5).to_dict(),
                    'total_unique_types': len(type_counts),
                    'type_distribution': type_counts.to_dict()
                }

        # Size analysis
        if 'args_size_bytes' in self.df.columns:
            size_data = self.df['args_size_bytes'].dropna()
            if not size_data.empty:
                analysis['size_analysis'] = {
                    'avg_args_size_bytes': size_data.mean(),
                    'max_args_size_bytes': size_data.max(),
                    'min_args_size_bytes': size_data.min(),
                    'large_args_calls': len(self.df[self.df['has_large_args'] == True]),
                    'size_distribution': {
                        'small (<1KB)': len(size_data[size_data < 1024]),
                        'medium (1KB-10KB)': len(size_data[(size_data >= 1024) & (size_data < 10240)]),
                        'large (>10KB)': len(size_data[size_data >= 10240])
                    }
                }

        # Security analysis
        if 'sensitive_args_detected' in self.df.columns:
            sensitive_calls = len(self.df[self.df['sensitive_args_detected'] == True])
            analysis['security_analysis'] = {
                'calls_with_sensitive_args': sensitive_calls,
                'sensitive_args_rate': sensitive_calls / total_calls if total_calls > 0 else 0
            }

        if 'has_file_args' in self.df.columns:
            file_calls = len(self.df[self.df['has_file_args'] == True])
            analysis['security_analysis']['calls_with_file_args'] = file_calls
            analysis['security_analysis']['file_args_rate'] = file_calls / total_calls if total_calls > 0 else 0

        # Tool-specific argument patterns
        if 'tool_name' in self.df.columns:
            tool_arg_patterns = self.df.groupby('tool_name').agg({
                'args_count': ['mean', 'max'],
                'args_complexity_score': 'mean',
                'has_large_args': 'sum',
                'sensitive_args_detected': 'sum'
            }).round(2)

            analysis['usage_patterns'] = {
                'tool_argument_patterns': tool_arg_patterns.to_dict(),
                'tools_with_complex_args': tool_arg_patterns[
                    (tool_arg_patterns[('args_complexity_score', 'mean')] > 0.5)
                ].index.tolist() if not tool_arg_patterns.empty else []
            }

        return analysis

    def get_argument_correlation_analysis(self) -> Dict[str, Any]:
        """
        Analyze correlations between arguments and execution performance.

        Returns:
            Dictionary containing argument-performance correlations
        """
        if self.df.empty:
            return {'error': 'No data available'}

        correlations = {}

        # Correlation between argument count and execution time
        if 'args_count' in self.df.columns and 'execution_time' in self.df.columns:
            correlation = self.df['args_count'].corr(self.df['execution_time'])
            correlations['args_count_vs_execution_time'] = {
                'correlation': correlation,
                'interpretation': self._interpret_correlation(correlation)
            }

        # Correlation between argument size and execution time
        if 'args_size_bytes' in self.df.columns and 'execution_time' in self.df.columns:
            correlation = self.df['args_size_bytes'].corr(self.df['execution_time'])
            correlations['args_size_vs_execution_time'] = {
                'correlation': correlation,
                'interpretation': self._interpret_correlation(correlation)
            }

        # Correlation between complexity and success rate
        if 'args_complexity_score' in self.df.columns and 'success' in self.df.columns:
            correlation = self.df['args_complexity_score'].corr(self.df['success'].astype(int))
            correlations['complexity_vs_success_rate'] = {
                'correlation': correlation,
                'interpretation': self._interpret_correlation(correlation)
            }

        # Performance comparison for different argument characteristics
        performance_comparisons = {}

        if 'has_large_args' in self.df.columns:
            large_args = self.df[self.df['has_large_args'] == True]
            small_args = self.df[self.df['has_large_args'] == False]

            if not large_args.empty and not small_args.empty:
                performance_comparisons['large_vs_small_args'] = {
                    'large_args_avg_time': large_args['execution_time'].mean(),
                    'small_args_avg_time': small_args['execution_time'].mean(),
                    'large_args_success_rate': large_args['success'].mean(),
                    'small_args_success_rate': small_args['success'].mean()
                }

        if 'sensitive_args_detected' in self.df.columns:
            sensitive_calls = self.df[self.df['sensitive_args_detected'] == True]
            regular_calls = self.df[self.df['sensitive_args_detected'] == False]

            if not sensitive_calls.empty and not regular_calls.empty:
                performance_comparisons['sensitive_vs_regular_args'] = {
                    'sensitive_avg_time': sensitive_calls['execution_time'].mean(),
                    'regular_avg_time': regular_calls['execution_time'].mean(),
                    'sensitive_success_rate': sensitive_calls['success'].mean(),
                    'regular_success_rate': regular_calls['success'].mean()
                }

        return {
            'correlations': correlations,
            'performance_comparisons': performance_comparisons
        }

    def get_result_analysis(self) -> Dict[str, Any]:
        """
        Analyze function call results and return patterns.

        Returns:
            Dictionary containing comprehensive result analysis
        """
        if self.df.empty:
            return {'error': 'No data available'}

        analysis = {
            'result_statistics': {},
            'type_analysis': {},
            'size_analysis': {},
            'quality_analysis': {}
        }

        total_calls = len(self.df)

        # Basic result statistics
        calls_with_results = len(self.df[self.df['has_result'] == True])
        analysis['result_statistics'] = {
            'total_calls': total_calls,
            'calls_with_results': calls_with_results,
            'calls_without_results': total_calls - calls_with_results,
            'result_rate': calls_with_results / total_calls if total_calls > 0 else 0
        }

        # Result type analysis
        if 'result_type' in self.df.columns:
            result_types = self.df['result_type'].dropna()
            if not result_types.empty:
                type_counts = result_types.value_counts()
                analysis['type_analysis'] = {
                    'most_common_types': type_counts.head(5).to_dict(),
                    'total_unique_types': len(type_counts),
                    'type_distribution': type_counts.to_dict()
                }

        # Result size analysis
        if 'result_size' in self.df.columns:
            size_data = self.df['result_size'].dropna()
            if not size_data.empty:
                analysis['size_analysis'] = {
                    'avg_result_size': size_data.mean(),
                    'max_result_size': size_data.max(),
                    'min_result_size': size_data.min(),
                    'median_result_size': size_data.median(),
                    'size_distribution': {
                        'small (<1KB)': len(size_data[size_data < 1024]),
                        'medium (1KB-100KB)': len(size_data[(size_data >= 1024) & (size_data < 102400)]),
                        'large (>100KB)': len(size_data[size_data >= 102400])
                    }
                }

        # Result quality analysis
        quality_metrics = {}

        if 'result_contains_errors' in self.df.columns:
            error_results = len(self.df[self.df['result_contains_errors'] == True])
            quality_metrics['results_with_errors'] = error_results
            quality_metrics['error_result_rate'] = error_results / total_calls if total_calls > 0 else 0

        if 'result_truncated' in self.df.columns:
            truncated_results = len(self.df[self.df['result_truncated'] == True])
            quality_metrics['truncated_results'] = truncated_results
            quality_metrics['truncation_rate'] = truncated_results / total_calls if total_calls > 0 else 0

        if 'result_complexity_score' in self.df.columns:
            complexity_data = self.df['result_complexity_score'].dropna()
            if not complexity_data.empty:
                quality_metrics['avg_result_complexity'] = complexity_data.mean()
                quality_metrics['high_complexity_results'] = len(complexity_data[complexity_data > 0.7])

        analysis['quality_analysis'] = quality_metrics

        return analysis

    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation coefficient."""
        if pd.isna(correlation):
            return "No correlation (insufficient data)"

        abs_corr = abs(correlation)
        direction = "positive" if correlation > 0 else "negative"

        if abs_corr < 0.1:
            return f"Very weak {direction} correlation"
        elif abs_corr < 0.3:
            return f"Weak {direction} correlation"
        elif abs_corr < 0.5:
            return f"Moderate {direction} correlation"
        elif abs_corr < 0.7:
            return f"Strong {direction} correlation"
        else:
            return f"Very strong {direction} correlation"
