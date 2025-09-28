# tau2-enhanced

Enhanced logging and analysis capabilities for tau2-bench evaluation framework

## Overview

This package extends the tau2-bench framework with comprehensive logging, state tracking, and detailed analysis capabilities for AI agent evaluations. It provides enhanced versions of tau2 domains that capture detailed execution logs, state snapshots, and performance metrics without modifying the original tau2-bench codebase.

## Features

- **Enhanced Environment Logging**: Comprehensive logging of all agent-environment interactions with execution times and state changes
- **State Snapshot Tracking**: Automatic capture of database state changes during tool calls
- **Extended Results Format**: Enhanced simulation results that inherit from tau2-bench with additional logging fields
- **Non-invasive Design**: Extends tau2-bench without modifying the original codebase
- **Flexible File Output**: Saves both standard tau2 results and detailed enhanced logs separately
- **CLI Integration**: Seamless integration with tau2 CLI through wrapper script
- **Programmatic API**: Direct Python API for enhanced simulation runs

## Installation

1. Clone or navigate to the tau2-enhanced directory
2. Install in development mode:

```bash
pip install -e .
```

## Usage

### Method 1: Using the tau2-enhanced wrapper (CLI)

Use the `tau2-enhanced` wrapper script which ensures enhanced domains are properly loaded:

```bash
./tau2-enhanced run --domain airline_enhanced --agent llm_agent --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash --task-ids 2 --num-trials 1
```

### Method 2: Programmatic API (Recommended for detailed logging)

Use the Python API for full control over enhanced logging:

```python
from tau2_enhanced import run_enhanced_simulation
from tau2.domains.airline.environment import get_tasks

# Load tasks
tasks = get_tasks()
test_task = next(task for task in tasks if task.id == "2")

# Run enhanced simulation
results, (main_path, logs_path) = run_enhanced_simulation(
    domain="airline_enhanced",
    tasks=[test_task],
    agent="llm_agent",
    user="user_simulator",
    llm_agent="gemini/gemini-2.5-flash",
    llm_user="gemini/gemini-2.5-flash",
    num_trials=1,
    save_dir="./enhanced_logs"
)

print(f"Results saved to: {main_path}")
print(f"Enhanced logs saved to: {logs_path}")
```

### Output Files

The enhanced system generates two types of files:
- **Standard Results**: `enhanced_results_TIMESTAMP.json` - Compatible with tau2-bench format
- **Enhanced Logs**: `enhanced_results_TIMESTAMP_enhanced_logs.json` - Detailed execution logs and state snapshots

## Available Enhanced Domains

- **`airline_enhanced`**: Enhanced version of the airline domain with comprehensive logging and monitoring

## Enhanced Logging Details

### Execution Logs
Each tool call is logged with:
- **tool_call_id**: Unique identifier for the tool call
- **execution_time**: Precise timing in seconds
- **success**: Whether the tool call succeeded
- **result_preview**: First 200 characters of the result
- **state_changed**: Whether the database state changed
- **validation_errors**: Any validation errors encountered

### State Snapshots
Captured when database state changes:
- **timestamp**: When the state change occurred
- **action_before**: Which tool call caused the change
- **pre_state_hash**: Database state before the change
- **post_state_hash**: Database state after the change
- **state_diff**: Human-readable description of changes

## Architecture

### Core Components
- `tau2_enhanced/environments/logging_environment.py`: LoggingEnvironment that wraps tau2 environments
- `tau2_enhanced/environments/domain_environments.py`: Enhanced domain registration
- `tau2_enhanced/data_model/enhanced_simulation.py`: Extended Results and SimulationRun classes
- `tau2_enhanced/enhanced_runner.py`: EnhancedRunner that captures logs from simulations

### Integration Pattern
The system uses monkey patching to intercept environment creation without modifying tau2-bench:
1. **Environment Wrapping**: Original environments are wrapped with LoggingEnvironment
2. **Log Capture**: Tool calls are intercepted and logged with detailed metrics
3. **Result Enhancement**: Standard tau2 results are extended with captured logs
4. **File Output**: Separate files for compatibility and enhanced data

## Development

### Adding New Enhanced Domains

1. Create enhanced environment function in `domain_environments.py`
2. Register the domain using `registry.register_domain()`
3. Register associated tasks using `registry.register_tasks()`
4. Test with the verification script



## Integration

The package integrates seamlessly with the existing tau2-bench ecosystem:

- **Non-invasive**: Does not modify the original tau2-bench codebase
- **Compatible**: Uses the same CLI interface and parameters
- **Flexible**: Enhanced domains can be used alongside standard tau2 domains
- **Extensible**: Easy to add new enhanced domains and logging features

## Requirements

- Python >= 3.10
- tau2-bench framework
- All dependencies listed in `pyproject.toml`

## Key Benefits

1. **Detailed Debugging**: See exactly what tools were called and how long they took
2. **State Tracking**: Monitor database changes throughout simulations
3. **Performance Analysis**: Identify bottlenecks in tool execution
4. **Audit Trail**: Complete record of agent-environment interactions
5. **Research Insights**: Deep analysis of agent behavior patterns

