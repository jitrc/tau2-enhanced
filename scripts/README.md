# Scripts

This directory contains scripts for analyzing the results of `tau2-bench` evaluations.

## `non_enhanced/analyze_breakdown.py`

This script provides a comprehensive breakdown metrics analysis of `tau2-bench` results.

### Usage

```bash
python scripts/non_enhanced/analyze_breakdown.py --results path/to/your/results.json [options]
```

### Options

*   `--export-csv`: Export the analysis results to CSV files.
*   `--task-details`: Show a detailed breakdown of performance for each task.
*   `--action-details`: Show a detailed analysis of each action taken by the agent.

### Example

```bash
python scripts/non_enhanced/analyze_breakdown.py --results baseline_airline_grok3.json --task-details
```

## `non_enhanced/failure_analysis.py`

This script performs a failure analysis on `tau2-bench` results to identify root causes of failures.

### Usage

```bash
python scripts/non_enhanced/failure_analysis.py path/to/your/results.json
```

### Example

```bash
python scripts/non_enhanced/failure_analysis.py baseline_airline_grok3.json
```
