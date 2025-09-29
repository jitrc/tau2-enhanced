# tau2-enhanced

**Advanced observability and analysis platform for tau2-bench AI agent evaluations**

## Overview

tau2-enhanced transforms tau2-bench with comprehensive structured logging, advanced analytics, and deep observability into AI agent behavior. It provides enhanced versions of all tau2 domains with rich event tracking, argument analysis, performance monitoring, and sophisticated analysis capabilities - all without modifying the original tau2-bench codebase.

## 🚀 Key Features

### **Structured Event Logging**
- **ExecutionLogger**: Comprehensive event logging with JSONL persistence and real-time export
- **ToolExecutionEvent**: Rich tool call tracking with timing, arguments, results, and metadata
- **StateChangeEvent**: Environment state transitions with detailed diff tracking
- **ContextReductionEvent**: Context management and token optimization monitoring

### **Advanced Analytics**
- **15+ Analysis Methods**: From basic metrics to advanced statistical analysis
- **Temporal Analysis**: Time-based patterns, trends, and performance evolution
- **Argument Intelligence**: Deep function call argument analysis and correlations
- **Error Pattern Detection**: Smart error categorization and root cause analysis
- **Performance Optimization**: Bottleneck identification and efficiency insights

### **Comprehensive Argument Tracking**
- **Function Signatures**: Required vs optional parameter usage analysis
- **Complexity Scoring**: Argument and result complexity measurement (0-1 scale)
- **Security Detection**: Automatic identification of sensitive data in arguments
- **Type Analysis**: Complete argument type distribution and patterns
- **Size Monitoring**: Argument and result size tracking with performance correlations

### **Automatic Domain Registration**
- **All Domains Enhanced**: airline_enhanced, retail_enhanced, telecom_enhanced, mock_enhanced
- **Zero Configuration**: Enhanced domains available immediately upon import
- **Seamless Integration**: Works with existing tau2-bench commands and workflows

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

### Method 3: Direct Analysis of Existing Logs

Analyze previously captured enhanced logs:

```python
from tau2_enhanced.analysis import LogAnalyzer

# Load and analyze enhanced logs
analyzer = LogAnalyzer("path/to/enhanced_logs.json")

# Get comprehensive analysis
analysis = analyzer.get_comprehensive_analysis()
print(f"Total tool calls: {analysis['basic_stats']['total_tool_calls']}")
print(f"Success rate: {analysis['basic_stats']['success_rate']:.2%}")

# Argument analysis
arg_analysis = analyzer.get_argument_analysis()
print(f"Most complex arguments: {arg_analysis['complexity_distribution']}")

# Performance insights
perf_analysis = analyzer.get_performance_analysis()
print(f"Slowest tools: {perf_analysis['slowest_tools']}")
```

### Output Files

The enhanced system generates two types of files:
- **Standard Results**: `enhanced_results_TIMESTAMP.json` - Compatible with tau2-bench format
- **Enhanced Logs**: `enhanced_results_TIMESTAMP_enhanced_logs.json` - Detailed execution logs and state snapshots

## Available Enhanced Domains

All tau2-bench domains are automatically enhanced upon import:

- **`airline_enhanced`**: Enhanced airline booking and management domain
- **`retail_enhanced`**: Enhanced retail customer service domain
- **`telecom_enhanced`**: Enhanced telecommunications support domain
- **`mock_enhanced`**: Enhanced mock/testing domain

## Enhanced Logging Details

### ToolExecutionEvent Structure
Each tool call is comprehensively tracked with:

```python
{
    # Core execution data
    "tool_name": "search_flights",
    "tool_call_id": "search_flights_1",
    "execution_time": 0.245,
    "success": true,
    "requestor": "assistant",
    "state_changed": true,

    # Enhanced argument tracking
    "args_count": 3,
    "args_size_bytes": 156,
    "args_complexity_score": 0.3,
    "args_types": {"departure": "str", "destination": "str", "date": "str"},
    "has_file_args": false,
    "has_large_args": false,
    "sensitive_args_detected": false,

    # Function signature analysis
    "required_args_provided": ["departure", "destination"],
    "optional_args_provided": ["date"],
    "missing_args": [],
    "unexpected_args": [],

    # Result analysis
    "result_size": 1024,
    "result_type": "dict",
    "result_complexity_score": 0.7,
    "result_contains_errors": false,
    "result_truncated": false
}
```

### StateChangeEvent Structure
Environment state transitions are captured with:

```python
{
    "state_type": "database",
    "action_trigger": "book_flight",
    "pre_state_hash": "abc123...",
    "post_state_hash": "def456...",
    "state_diff": "Added 1 booking record, updated customer balance",
    "change_summary": "Flight booking completed successfully"
}
```

### State Snapshots
Detailed environment snapshots captured at key moments:
- **Before/after each tool call**
- **On state changes**
- **At simulation start/end**
- **On errors or exceptions**

## Analysis Capabilities

### Statistical Analysis Methods

1. **Basic Statistics**: Success rates, timing distributions, error counts
2. **Confidence Intervals**: Statistical significance of performance metrics
3. **Correlation Analysis**: Relationships between arguments and outcomes
4. **Distribution Analysis**: Tool usage patterns and frequency distributions
5. **Gini Coefficient**: Inequality in tool usage and performance
6. **Shannon Diversity**: Diversity of tool calls and argument patterns
7. **Temporal Analysis**: Performance trends over time
8. **Error Pattern Analysis**: Error categorization and root cause analysis

### Performance Analytics

```python
# Get performance bottlenecks
bottlenecks = analyzer.get_performance_bottlenecks()
print(f"Slowest operations: {bottlenecks['slowest_operations']}")

# Analyze tool efficiency
efficiency = analyzer.get_tool_efficiency_metrics()
print(f"Most efficient tools: {efficiency['top_performers']}")

# Get argument correlations
correlations = analyzer.get_argument_correlation_analysis()
print(f"Performance predictors: {correlations['performance_predictors']}")
```

### Argument Intelligence

The system provides deep insights into function call patterns:

- **Complexity Scoring**: 0-1 scale based on argument count, types, and sizes
- **Security Detection**: Automatic identification of sensitive parameters
- **Usage Patterns**: Required vs optional parameter utilization
- **Performance Correlations**: How argument complexity affects execution time
- **Type Analysis**: Distribution of argument types across tool calls

## Architecture

### Core Components

- **`tau2_enhanced/logging/`**: Structured event logging system
  - `execution_logger.py`: Main event logger with JSONL persistence
  - `state_tracker.py`: Environment state monitoring and diff tracking
  - `events.py`: Event type definitions and serialization

- **`tau2_enhanced/analysis/`**: Analytics and intelligence system
  - `analyzer.py`: Comprehensive log analysis with 15+ methods
  - `visualizer.py`: Data visualization and reporting

- **`tau2_enhanced/environments/`**: Environment enhancement system
  - `logging_environment.py`: LoggingEnvironment wrapper for tau2 environments
  - `domain_environments.py`: Automatic domain registration system

- **`tau2_enhanced/domain_registration.py`**: Core domain discovery and registration

### Integration Pattern

The system uses monkey patching to intercept environment creation without modifying tau2-bench:

1. **Automatic Discovery**: Scans for available tau2 domains
2. **Environment Wrapping**: Original environments wrapped with LoggingEnvironment
3. **Log Capture**: Tool calls intercepted and logged with detailed metrics
4. **Result Enhancement**: Standard tau2 results extended with captured logs
5. **Non-Invasive**: Zero modification to existing tau2-bench codebase

### Domain Registration System

```python
from tau2_enhanced.domain_registration import EnhancedDomainRegistry

# Automatic registration of all available domains
registry = EnhancedDomainRegistry()
registered = registry.register_all_available_domains()
print(f"Registered domains: {list(registered.keys())}")

# Manual domain registration
registry.register_enhanced_domain(
    domain_name="custom",
    original_get_environment=custom_get_environment,
    original_get_tasks=custom_get_tasks
)
```

## Development

### Adding New Enhanced Domains

1. **Implement domain functions** in `domain_environments.py`:
```python
def get_custom_enhanced_environment(*args, **kwargs):
    original_env = get_custom_environment(*args, **kwargs)
    return LoggingEnvironment(original_env, log_file="custom.jsonl")
```

2. **Register the domain**:
```python
registry.register_enhanced_domain(
    domain_name="custom",
    original_get_environment=get_custom_environment,
    original_get_tasks=get_custom_tasks
)
```

3. **Test integration**:
```bash
./tau2-enhanced run --domain custom_enhanced --num-trials 1
```

### Custom Event Types

Extend the logging system with custom events:

```python
from tau2_enhanced.logging.events import ExecutionEvent

@dataclass
class CustomAnalysisEvent(ExecutionEvent):
    analysis_type: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self.source = f"analysis:{self.analysis_type}"
```


## API Reference

### ExecutionLogger

```python
from tau2_enhanced.logging import ExecutionLogger

logger = ExecutionLogger(
    log_file="execution.jsonl",
    auto_flush=True,
    console_output=False
)

# Log tool execution
logger.log_tool_execution(
    tool_name="search_flights",
    success=True,
    execution_time=0.5,
    tool_args={"departure": "NYC", "destination": "LAX"},
    result=flight_results
)

# Get statistics
stats = logger.get_statistics()
print(f"Total events: {stats['total_events']}")
```

### StateTracker

```python
from tau2_enhanced.logging import StateTracker

tracker = StateTracker(
    max_snapshots=1000,
    auto_snapshot=True,
    track_state_hash=True
)

# Create state snapshot
tracker.create_snapshot(
    state_data={"bookings": 5, "customers": 100},
    action_trigger="book_flight",
    metadata={"tool": "book_flight", "success": True}
)
```

### LogAnalyzer

```python
from tau2_enhanced.analysis import LogAnalyzer

analyzer = LogAnalyzer("enhanced_logs.json")

# Comprehensive analysis
analysis = analyzer.get_comprehensive_analysis()

# Specific analysis types
perf_analysis = analyzer.get_performance_analysis()
arg_analysis = analyzer.get_argument_analysis()
error_analysis = analyzer.get_error_analysis()
temporal_analysis = analyzer.get_temporal_analysis()
```

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

1. **Deep Observability**: Complete visibility into agent-environment interactions
2. **Performance Optimization**: Identify bottlenecks and efficiency improvements
3. **Behavioral Analysis**: Understand agent decision patterns and strategies
4. **Argument Intelligence**: Comprehensive function call argument analysis
5. **Error Diagnostics**: Smart error categorization and root cause analysis
6. **Research Insights**: Statistical analysis for academic and industry research
7. **Production Monitoring**: Real-time streaming logs for operational use
8. **Audit Trail**: Complete, immutable record of all interactions

