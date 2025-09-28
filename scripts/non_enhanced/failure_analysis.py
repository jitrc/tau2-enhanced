#!/usr/bin/env python3
"""
Failure analysis for tau2-bench failures.
"""

import sys
from pathlib import Path
import pandas as pd

from tau2.data_model.simulation import Results
from tau2.metrics.break_down_metrics import result_reward_analysis, result_reward_actions_analysis
from tau2.utils import DATA_DIR

def investigate_specific_task(results: Results, task_id: str):
    """Investigate a specific failing task in detail."""
    print(f"\n🔍 DEEP DIVE: Task {task_id}")
    print("=" * 50)

    # Get the task definition
    task = next((t for t in results.tasks if t.id == task_id), None)
    if not task:
        print(f"❌ Task {task_id} not found")
        return

    # Get all simulations for this task
    task_sims = [s for s in results.simulations if s.task_id == task_id]

    print(f"📊 Task Overview:")
    print(f"  Description: {task.description.purpose}")
    print(f"  Simulations: {len(task_sims)}")

    if task.evaluation_criteria:
        print(f"\n📋 Requirements:")
        if task.evaluation_criteria.actions:
            print(f"  Actions required: {len(task.evaluation_criteria.actions)}")
            for i, action in enumerate(task.evaluation_criteria.actions, 1):
                print(f"    {i}. {action.name}(...)")

        if task.evaluation_criteria.communicate_info:
            print(f"  Communication required: {len(task.evaluation_criteria.communicate_info)} items")
            for info in task.evaluation_criteria.communicate_info:
                print(f"    - Must communicate: '{info}'")

    # Analyze failures
    print(f"\n❌ Failure Analysis:")
    for sim in task_sims:
        result = "✅ SUCCESS" if sim.reward_info.reward >= 0.5 else "❌ FAILURE"
        print(f"  Trial {sim.trial}: {result} (reward: {sim.reward_info.reward:.3f})")

        if sim.reward_info.reward < 0.5:
            print(f"    Duration: {sim.duration:.1f}s, Messages: {len(sim.messages)}")
            print(f"    Termination: {sim.termination_reason.value}")

            # Show what failed
            if sim.reward_info.reward_breakdown:
                failed_components = [f"{k.value}: {v:.3f}"
                                   for k, v in sim.reward_info.reward_breakdown.items()
                                   if v < 0.5]
                if failed_components:
                    print(f"    Failed components: {', '.join(failed_components)}")

            # Show action failures
            if sim.reward_info.action_checks:
                failed_actions = [check.action.name
                                for check in sim.reward_info.action_checks
                                if not check.action_match]
                if failed_actions:
                    print(f"    Failed actions: {', '.join(failed_actions)}")

def analyze_action_patterns(results: Results, action_name: str):
    """Analyze patterns for a specific failing action."""
    print(f"\n⚡ ACTION ANALYSIS: {action_name}")
    print("=" * 50)

    try:
        action_df = result_reward_actions_analysis(results)
    except:
        print("❌ Could not load action analysis data")
        return

    if action_df is None or len(action_df) == 0:
        print("❌ No action data available")
        return

    action_data = action_df[action_df['action_name'] == action_name]
    if len(action_data) == 0:
        print(f"❌ No data found for action {action_name}")
        return

    total = len(action_data)
    failures = len(action_data[action_data['action_match'] == False])

    print(f"📊 {action_name} Performance:")
    print(f"  Total attempts: {total}")
    print(f"  Failures: {failures} ({failures/total*100:.1f}%)")
    print(f"  Success rate: {(total-failures)/total*100:.1f}%")

    # Show tasks where this action commonly fails
    failed_data = action_data[action_data['action_match'] == False]
    if len(failed_data) > 0:
        failing_tasks = failed_data['task_id'].value_counts().head(5)
        print(f"\n🎯 Tasks with most {action_name} failures:")
        for task_id, count in failing_tasks.items():
            total_for_task = len(action_data[action_data['task_id'] == task_id])
            print(f"  Task {task_id}: {count}/{total_for_task} failures ({count/total_for_task*100:.1f}%)")

def show_task_complexity_impact(results: Results):
    """Show how task complexity affects success rates."""
    print(f"\n📊 COMPLEXITY vs SUCCESS ANALYSIS")
    print("=" * 50)

    reward_df = result_reward_analysis(results)

    # Group by complexity metrics
    complexity_analysis = reward_df.groupby('num_write_action').agg({
        'success': ['count', 'mean'],
        'communication': 'mean',
        'database': 'mean'
    }).round(3)

    print("Success rates by number of write actions required:")
    print("Actions | Count | Success | Communication | Database")
    print("--------|-------|---------|---------------|----------")

    for actions in sorted(reward_df['num_write_action'].unique()):
        subset = reward_df[reward_df['num_write_action'] == actions]
        count = len(subset)
        success = subset['success'].mean()
        comm = subset['communication'].mean()
        db = subset['database'].mean()
        print(f"   {actions:2d}   |  {count:3d}  |  {success:.3f}  |    {comm:.3f}     |  {db:.3f}")

def identify_root_causes(results: Results):
    """Identify the most likely root causes of failures."""
    print(f"\n🎯 ROOT CAUSE IDENTIFICATION")
    print("=" * 50)

    reward_df = result_reward_analysis(results)
    failed_df = reward_df[reward_df['success'] == False]

    if len(failed_df) == 0:
        print("✅ No failures to analyze!")
        return

    print(f"Analyzing {len(failed_df)} failed simulations...")

    # Primary failure modes
    print(f"\n🔍 Primary Failure Modes:")

    # Communication failures
    comm_failures = len(failed_df[failed_df['communication'] == False])
    print(f"  Communication failures: {comm_failures}/{len(failed_df)} ({comm_failures/len(failed_df)*100:.1f}%)")

    # Database failures
    db_failures = len(failed_df[failed_df['database'] == False])
    print(f"  Database failures: {db_failures}/{len(failed_df)} ({db_failures/len(failed_df)*100:.1f}%)")

    # Action execution failures
    action_failures = len(failed_df[failed_df['num_correct_write_action'] < failed_df['num_write_action']])
    print(f"  Action execution failures: {action_failures}/{len(failed_df)} ({action_failures/len(failed_df)*100:.1f}%)")

    # Identify the "killer" complexity threshold
    print(f"\n⚠️  Critical Insights:")

    # Tasks by complexity
    no_action_success = reward_df[reward_df['num_write_action'] == 0]['success'].mean()
    action_success = reward_df[reward_df['num_write_action'] > 0]['success'].mean()

    print(f"  No-action tasks succeed at {no_action_success*100:.1f}% rate")
    print(f"  Action-required tasks succeed at {action_success*100:.1f}% rate")
    print(f"  → {(no_action_success - action_success)*100:.1f}percentage point performance drop when actions required")

    # Most problematic actions
    try:
        action_df = result_reward_actions_analysis(results)
        if action_df is not None:
            action_failure_rates = action_df.groupby('action_name')['action_match'].agg(['count', 'mean']).round(3)
            action_failure_rates['failure_rate'] = 1 - action_failure_rates['mean']
            worst_actions = action_failure_rates[action_failure_rates['count'] >= 5].sort_values('failure_rate', ascending=False)

            print(f"\n🚨 Most Problematic Actions (min 5 attempts):")
            for action_name, row in worst_actions.head(5).iterrows():
                print(f"  {action_name}: {row['failure_rate']*100:.1f}% failure rate ({row['count']} attempts)")
    except:
        print(f"  (Could not analyze individual action failure rates)")

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

def main():
    if len(sys.argv) != 2:
        print("Usage: python failure_analysis.py <results.json>")
        sys.exit(1)
    
    results = load_results(sys.argv[1])


    # High-level analysis
    identify_root_causes(results)
    show_task_complexity_impact(results)

    # Drill down into worst performing areas
    reward_df = result_reward_analysis(results)
    worst_tasks = reward_df.groupby('task_id')['success'].mean().sort_values().head(3)

    print(f"\n🔍 INVESTIGATING WORST TASKS")
    print("=" * 50)

    for task_id in worst_tasks.index:
        investigate_specific_task(results, task_id)

    # Analyze most problematic actions
    try:
        action_df = result_reward_actions_analysis(results)
        if action_df is not None:
            action_failure_rates = action_df.groupby('action_name')['action_match'].mean().sort_values()
            worst_action = action_failure_rates.index[0]
            analyze_action_patterns(results, worst_action)
    except:
        pass

    print(f"\n✅ Root cause analysis complete!")


if __name__ == "__main__":
    main()