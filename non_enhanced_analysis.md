# Non-Enhanced Analysis Scripts

## Breakdown Analysis

The `scripts/non_enhanced/analyze_breakdown.py` script provides comprehensive analysis of tau2-bench results:

```bash
# Analyze results with relative paths
python scripts/non_enhanced/analyze_breakdown.py --results scripts/non_enhanced/baseline_airline_grok3.json

# Or from tau2-bench data directory
python scripts/non_enhanced/analyze_breakdown.py --results tau2/results/final/claude-3-7-sonnet-20250219_airline_default_gpt-4.1-2025-04-14_4trials.json

# With additional options
python scripts/non_enhanced/analyze_breakdown.py --results baseline_airline_grok3.json --export-csv --task-details --action-details
```

The script automatically handles path resolution:
1. First tries relative paths from current directory
2. Falls back to relative paths from tau2-bench DATA_DIR
3. Supports both local files and files in the original tau2-bench data structure

**Analysis Features:**
- Basic success rate summaries
- Action complexity analysis
- Failure pattern identification
- Trial consistency evaluation
- Task-by-task breakdown
- Detailed action analysis
- CSV export capabilities