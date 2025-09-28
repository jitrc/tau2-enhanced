# tau2-enhanced

Enhanced logging capabilities for tau2-bench evaluation framework

## Overview

This package extends the tau2-bench framework with enhanced logging and monitoring capabilities for AI agent evaluations. It provides enhanced versions of tau2 domains with comprehensive logging, debugging capabilities, and detailed execution tracking.

## Features

- **Enhanced Environment Logging**: Comprehensive logging of agent-environment interactions
- **Domain-specific Enhancements**: Starting with `airline_enhanced` domain with full compatibility
- **Detailed Execution Tracking**: Enhanced monitoring and analysis capabilities
- **CLI Integration**: Seamless integration with tau2 CLI through wrapper script
- **Backward Compatibility**: Full compatibility with existing tau2 workflows

## Installation

1. Clone or navigate to the tau2-enhanced directory
2. Install in development mode:

```bash
pip install -e .
```

## Usage

### Using the tau2-enhanced wrapper (Recommended)

Use the `tau2-enhanced` wrapper script which ensures enhanced domains are properly loaded:

```bash
./tau2-enhanced run --domain airline_enhanced --agent llm_agent --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash --num-tasks 1 --num-trials 1
```

### Domain Verification

Check if enhanced domains are properly registered:

```bash
python check_domain.py
```

## Available Enhanced Domains

- **`airline_enhanced`**: Enhanced version of the airline domain with comprehensive logging and monitoring

## Architecture

- `tau2_enhanced/environments/logging_environment.py`: Core enhanced environment wrapper
- `tau2_enhanced/environments/domain_environments.py`: Domain registration and enhanced environment factories
- `tau2-enhanced`: CLI wrapper script for seamless integration
- `check_domain.py`: Domain registration verification utility

## Development

### Adding New Enhanced Domains

1. Create enhanced environment function in `domain_environments.py`
2. Register the domain using `registry.register_domain()`
3. Register associated tasks using `registry.register_tasks()`
4. Test with the verification script

### Testing

Run a quick test to verify everything works:

```bash
./tau2-enhanced run --domain airline_enhanced --agent llm_agent --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash --num-tasks 1 --num-trials 1
```

## Integration

The package integrates seamlessly with the existing tau2-bench ecosystem:

- Uses the same CLI interface and parameters
- Compatible with all existing agents and models
- Maintains full compatibility with tau2 evaluation pipeline
- Enhanced domains can be used alongside standard tau2 domains

## Requirements

- Python >= 3.10
- tau2-bench framework
- All dependencies listed in `pyproject.toml`

