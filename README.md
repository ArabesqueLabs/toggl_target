# Toggl Target v2.0

[![CI/CD](https://github.com/mos3abof/toggl_target/workflows/CI/badge.svg)](https://github.com/mos3abof/toggl_target/actions)
[![codecov](https://codecov.io/gh/mos3abof/toggl_target/branch/main/graph/badge.svg)](https://codecov.io/gh/mos3abof/toggl_target)
[![PyPI version](https://badge.fury.io/py/toggl-target.svg)](https://badge.fury.io/py/toggl-target)

A modern Python library and CLI for calculating work hour targets from Toggl time tracking data.

## Features

- 🚀 **Modern Python 3.8+** with type hints and dataclasses
- 🎯 **Accurate calculations** for monthly targets and daily requirements
- 🛠 **Rich CLI interface** with beautiful terminal output
- ⚙️ **Flexible configuration** via YAML files or environment variables
- 📊 **Multiple output formats** (terminal, JSON, YAML)
- 🧪 **Comprehensive testing** with pytest
- 📦 **Easy installation** with UV/pip

## Installation

### Using UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install toggl-target
uv add toggl-target
```

### Using pip

```bash
pip install toggl-target
```

## Quick Start

### 1. Initialize Configuration

```bash
# Create a default configuration file
toggl-target init

# Or specify a custom path
toggl-target init my-config.yaml
```

### 2. Configure Your API Token

Edit the generated `toggl-target.yaml` file:

```yaml
api:
  api_token: "YOUR_TOGGL_API_TOKEN_HERE"  # Get from https://track.toggl.com/profile
  timezone: "+00:00"

working_time:
  working_hours_per_day: 8.0
  business_days: [MON, TUE, WED, THU, FRI]
  tolerance_percentage: 0.1
```

### 3. Check Your Status

```bash
# Show current progress
toggl-target status

# Get detailed report in JSON format
toggl-target report --format json

# Get detailed report in YAML format  
toggl-target report --format yaml
```

### 4. Use as a Library

```python
from toggl_target import TogglAPI, TargetCalculator, ConfigManager

# Load configuration
config_manager = ConfigManager()
working_config, api_config = config_manager.load_config()

# Initialize API and calculator
api = TogglAPI(api_config)
calculator = TargetCalculator(working_config)

# Get current progress
achieved_hours = api.get_hours_tracked(
    start_date=calculator.month_start,
    end_date=calculator.now
)

target, min_hours, req_hours = calculator.get_daily_targets(achieved_hours)
print(f"Achieved: {target.achieved_hours:.2f}h")
print(f"Progress: {target.achieved_percentage*100:.1f}%")
```

## Configuration

### Configuration File Locations

Toggl Target looks for configuration files in this order:

1. `toggl-target.yaml` (current directory)
2. `toggl-target.yml` (current directory)  
3. `.toggl-target.yaml` (current directory)
4. `~/.config/toggl-target/config.yaml`
5. `~/.toggl-target.yaml`

### Environment Variables

You can override configuration with environment variables:

```bash
export TOGGL_API_TOKEN="your_token_here"
export TOGGL_TIMEZONE="+02:00"
export WORKING_HOURS_PER_DAY="7.5"
export TOLERANCE_PERCENTAGE="0.15"
export BUSINESS_DAYS="MON,TUE,WED,THU,FRI"
```

## CLI Commands

### `status`
Show current progress and daily targets.

```bash
toggl-target status [--config PATH] [--verbose]
```

### `report`  
Generate detailed reports.

```bash
toggl-target report [--format table|json|yaml] [--config PATH] [--verbose]
```

### `init`
Initialize configuration file.

```bash
toggl-target init [PATH] [--force]
```

### `version`
Show version information.

```bash
toggl-target version
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/mos3abof/toggl_target.git
cd toggl_target

# Create virtual environment with UV
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install in development mode
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/toggl_target --cov-report=html

# Run specific test file
uv run pytest tests/test_models.py
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## Migration from v1.x

If you're migrating from the old Python 2.7 version:

1. **Configuration**: The old `config.py` file is no longer used. Use `toggl-target init` to create a modern YAML config.

2. **Python Version**: Requires Python 3.8+ (was Python 2.7)

3. **Installation**: Use UV or pip (was manual requirements.txt)

4. **CLI**: New commands and options. Run `toggl-target --help` to see all options.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the GPL-2.0 License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Support

If you have trouble using this code:

- 📧 Email: toggl@mos3abof.com
- 🐛 Issues: [GitHub Issues](https://github.com/mos3abof/toggl_target/issues)
- 📖 Documentation: [Wiki](https://github.com/mos3abof/toggl_target/wiki)

## Acknowledgments

- Thanks to all [contributors](https://github.com/mos3abof/toggl_target/graphs/contributors) who have helped improve this project.
- Built with ❤️ using modern Python tools: UV, Pydantic, Click, Rich, and pytest.