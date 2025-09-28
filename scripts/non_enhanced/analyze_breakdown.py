#!/usr/bin/env python3
"""
Comprehensive breakdown metrics analysis script for tau2-bench results.

Usage:
    python analyze_breakdown.py --results path/to/results.json [options]

Examples:
    python analyze_breakdown.py --results baseline_airline_grok3.json
    python analyze_breakdown.py --results baseline_airline_grok3.json --export-csv
    python analyze_breakdown.py --results baseline_airline_grok3.json --task-details
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

# Add src to path for imports
sys.path.append('src')

from tau2.data_model.simulation import Results
from tau2.metrics.break_down_metrics import result_reward_analysis, result_reward_actions_analysis
from tau2.metrics.agent_metrics import compute_metrics
from tau2.utils import DATA_DIR


def load_results(results_path: str) -> Results:
    """Load results from JSON file."""
    path = Path(results_path)

    # If the path is relative, try resolving it relative to current directory first
    if not path.is_absolute():
        # Try relative to current directory
        if path.exists():
            path = path.resolve()
        else:
            # If not found, try relative to DATA_DIR
            path = DATA_DIR / results_path

    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")

    print(f"📁 Loading results from: {path}")
    return Results.load(path)


def basic_summary(df: pd.DataFrame) -> None:
    """Print basic summary statistics."""
    print("\n🎯 BASIC SUMMARY")
    print("=" * 50)

    total_simulations = len(df)
    unique_tasks = df['task_id'].nunique()
    avg_trials = df.groupby('task_id').size().mean()

    print(f"Total simulations: {total_simulations}")
    print(f"Unique tasks: {unique_tasks}")
    print(f"Average trials per task: {avg_trials:.1f}")

    # Success metrics
    overall_success = df['success'].mean()
    comm_success = df['communication'].mean() if 'communication' in df.columns else None
    env_success = df['environment'].mean() if 'environment' in df.columns else None
    db_success = df['database'].mean() if 'database' in df.columns else None

    print(f"\n📊 Success Rates:")
    print(f"  Overall: {overall_success:.3f} ({overall_success*100:.1f}%)")
    if comm_success is not None:
        print(f"  Communication: {comm_success:.3f} ({comm_success*100:.1f}%)")
    if env_success is not None:
        print(f"  Environment: {env_success:.3f} ({env_success*100:.1f}%)")
    if db_success is not None:
        print(f"  Database: {db_success:.3f} ({db_success*100:.1f}%)")


def action_analysis(df: pd.DataFrame) -> None:
    """Analyze write action performance."""
    print("\n⚡ ACTION ANALYSIS")
    print("=" * 50)

    if 'num_write_action' not in df.columns:
        print("No write action data available")
        return

    # Action statistics
    avg_actions = df['num_write_action'].mean()
    avg_correct = df['num_correct_write_action'].mean()
    action_accuracy = avg_correct / avg_actions if avg_actions > 0 else 0

    print(f"Average write actions per task: {avg_actions:.2f}")
    print(f"Average correct write actions: {avg_correct:.2f}")
    print(f"Write action accuracy: {action_accuracy:.3f} ({action_accuracy*100:.1f}%)")

    # Success by action complexity
    print(f"\n📈 Success Rate by Action Complexity:")
    action_complexity = df.groupby('num_write_action')['success'].agg(['count', 'mean']).round(3)
    action_complexity.columns = ['Count', 'Success_Rate']
    print(action_complexity)

    # Tasks with no actions vs tasks with actions
    no_action_tasks = df[df['num_write_action'] == 0]
    action_tasks = df[df['num_write_action'] > 0]

    if len(no_action_tasks) > 0 and len(action_tasks) > 0:
        print(f"\n🔍 Action vs No-Action Comparison:")
        print(f"  No-action tasks success: {no_action_tasks['success'].mean():.3f}")
        print(f"  Action-required tasks success: {action_tasks['success'].mean():.3f}")


def task_breakdown(df: pd.DataFrame) -> None:
    """Break down performance by individual tasks."""
    print("\n📋 TASK-BY-TASK BREAKDOWN")
    print("=" * 50)

    task_summary = df.groupby('task_id').agg({
        'success': ['count', 'mean', 'std'],
        'communication': 'mean' if 'communication' in df.columns else lambda x: None,
        'num_write_action': 'mean' if 'num_write_action' in df.columns else lambda x: None,
        'num_correct_write_action': 'mean' if 'num_correct_write_action' in df.columns else lambda x: None,
    }).round(3)

    # Flatten column names
    task_summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in task_summary.columns]

    # Sort by success rate
    task_summary = task_summary.sort_values('success_mean', ascending=False)

    print("Top performing tasks:")
    print(task_summary.head(10))

    print(f"\nWorst performing tasks:")
    print(task_summary.tail(5))


def failure_analysis(df: pd.DataFrame) -> None:
    """Analyze failure patterns."""
    print("\n🔍 FAILURE ANALYSIS")
    print("=" * 50)

    failed_tasks = df[df['success'] == False]

    if len(failed_tasks) == 0:
        print("🎉 No failures found! All tasks succeeded.")
        return

    print(f"Total failures: {len(failed_tasks)} / {len(df)} ({len(failed_tasks)/len(df)*100:.1f}%)")

    # Failure breakdown by component
    if 'communication' in df.columns:
        comm_failures = failed_tasks[failed_tasks['communication'] == False]
        print(f"Communication failures: {len(comm_failures)} ({len(comm_failures)/len(failed_tasks)*100:.1f}% of failures)")

    if 'environment' in df.columns:
        env_failures = failed_tasks[failed_tasks['environment'] == False]
        print(f"Environment failures: {len(env_failures)} ({len(env_failures)/len(failed_tasks)*100:.1f}% of failures)")

    if 'database' in df.columns:
        db_failures = failed_tasks[failed_tasks['database'] == False]
        print(f"Database failures: {len(db_failures)} ({len(db_failures)/len(failed_tasks)*100:.1f}% of failures)")

    # Action-related failures
    if 'num_write_action' in df.columns:
        action_failures = failed_tasks[failed_tasks['num_correct_write_action'] < failed_tasks['num_write_action']]
        print(f"Action execution failures: {len(action_failures)} ({len(action_failures)/len(failed_tasks)*100:.1f}% of failures)")

    # Most problematic tasks
    failure_by_task = failed_tasks['task_id'].value_counts().head(5)
    print(f"\nMost problematic tasks:")
    for task_id, count in failure_by_task.items():
        total_for_task = len(df[df['task_id'] == task_id])
        failure_rate = count / total_for_task
        print(f"  Task {task_id}: {count}/{total_for_task} failures ({failure_rate*100:.1f}%)")


def action_details_analysis(action_df: Optional[pd.DataFrame]) -> None:
    """Analyze detailed action performance."""
    if action_df is None or len(action_df) == 0:
        print("\n⚠️  No detailed action data available")
        return

    print("\n🎬 DETAILED ACTION ANALYSIS")
    print("=" * 50)

    # Action accuracy by type
    action_accuracy = action_df.groupby('action_name')['action_match'].agg(['count', 'mean']).round(3)
    action_accuracy.columns = ['Count', 'Accuracy']
    action_accuracy = action_accuracy.sort_values('Accuracy', ascending=False)

    print("Action accuracy by type:")
    print(action_accuracy)

    # Actions by requestor
    requestor_stats = action_df.groupby('requestor')['action_match'].agg(['count', 'mean']).round(3)
    requestor_stats.columns = ['Count', 'Accuracy']

    print(f"\nPerformance by requestor:")
    print(requestor_stats)

    # Most common failed actions
    failed_actions = action_df[action_df['action_match'] == False]
    if len(failed_actions) > 0:
        failed_action_counts = failed_actions['action_name'].value_counts().head(5)
        print(f"\nMost commonly failed actions:")
        for action_name, count in failed_action_counts.items():
            total_attempts = len(action_df[action_df['action_name'] == action_name])
            failure_rate = count / total_attempts
            print(f"  {action_name}: {count}/{total_attempts} failures ({failure_rate*100:.1f}%)")


def trial_consistency_analysis(df: pd.DataFrame) -> None:
    """Analyze consistency across trials."""
    print("\n🔄 TRIAL CONSISTENCY ANALYSIS")
    print("=" * 50)

    if 'trial' not in df.columns:
        print("No trial data available")
        return

    # Success rate by trial
    trial_stats = df.groupby('trial')['success'].agg(['count', 'mean', 'std']).round(3)
    trial_stats.columns = ['Count', 'Success_Rate', 'Std_Dev']

    print("Performance by trial:")
    print(trial_stats)

    # Task consistency (std dev of success across trials)
    task_consistency = df.groupby('task_id')['success'].std().fillna(0)
    inconsistent_tasks = task_consistency[task_consistency > 0.3].sort_values(ascending=False)

    if len(inconsistent_tasks) > 0:
        print(f"\nMost inconsistent tasks (high variance across trials):")
        print(inconsistent_tasks.head(10))
    else:
        print(f"\n✅ All tasks show consistent performance across trials")


def export_data(df: pd.DataFrame, action_df: Optional[pd.DataFrame], results_path: str) -> None:
    """Export data to CSV files."""
    base_path = Path(results_path).stem

    # Export reward breakdown
    reward_csv = f"{base_path}_reward_breakdown.csv"
    df.to_csv(reward_csv, index=False)
    print(f"📊 Exported reward breakdown to: {reward_csv}")

    # Export action details if available
    if action_df is not None and len(action_df) > 0:
        action_csv = f"{base_path}_action_breakdown.csv"
        action_df.to_csv(action_csv, index=False)
        print(f"🎬 Exported action breakdown to: {action_csv}")


def main():
    parser = argparse.ArgumentParser(description="Analyze tau2-bench breakdown metrics")
    parser.add_argument("--results", type=str, required=True, help="Path to results JSON file")
    parser.add_argument("--export-csv", action="store_true", help="Export analysis to CSV files")
    parser.add_argument("--task-details", action="store_true", help="Show detailed per-task analysis")
    parser.add_argument("--action-details", action="store_true", help="Show detailed action analysis")

    args = parser.parse_args()

    try:
        # Load results
        results = load_results(args.results)

        # Get breakdown dataframes
        print("🔄 Computing breakdown metrics...")
        reward_df = result_reward_analysis(results)
        action_df = None

        try:
            action_df = result_reward_actions_analysis(results)
        except Exception as e:
            print(f"⚠️  Could not load action details: {e}")

        # Run analysis
        basic_summary(reward_df)
        action_analysis(reward_df)
        failure_analysis(reward_df)
        trial_consistency_analysis(reward_df)

        if args.task_details:
            task_breakdown(reward_df)

        if args.action_details:
            action_details_analysis(action_df)

        # Standard metrics for comparison
        print("\n🏆 STANDARD METRICS (for comparison)")
        print("=" * 50)
        standard_metrics = compute_metrics(results)
        print(f"Average reward: {standard_metrics.avg_reward:.3f}")
        for k, pass_k in standard_metrics.pass_hat_ks.items():
            print(f"Pass@{k}: {pass_k:.3f}")
        print(f"Average agent cost: ${standard_metrics.avg_agent_cost:.4f}")

        # Export if requested
        if args.export_csv:
            export_data(reward_df, action_df, args.results)

        print(f"\n✅ Analysis complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()