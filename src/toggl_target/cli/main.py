"""Main CLI interface for Toggl Target."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from toggl_target.config import ConfigManager, ConfigError
from toggl_target.core import TogglAPI, TargetCalculator, TogglAPIError
from toggl_target.utils import success_text, error_text, warning_text, info_text
from toggl_target.cli.formatters import StatusFormatter, ReportFormatter


# Setup console for rich output
console = Console()

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="2.0.0", prog_name="toggl-target")
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool):
    """Toggl Target - Modern time tracking target calculator."""
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Verbose mode enabled")
    
    # Initialize context
    ctx.ensure_object(dict)
    
    if config:
        ctx.obj['config_path'] = Path(config)
    
    # Load configuration
    try:
        config_manager = ConfigManager(ctx.obj.get('config_path'))
        working_config, api_config = config_manager.load_config()
        
        ctx.obj['config_manager'] = config_manager
        ctx.obj['working_config'] = working_config
        ctx.obj['api_config'] = api_config
        
    except ConfigError as e:
        console.print(error_text(f"Configuration error: {e}"))
        sys.exit(1)
    except Exception as e:
        console.print(error_text(f"Unexpected error loading configuration: {e}"))
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context):
    """Show current status and progress."""
    try:
        api_config = ctx.obj['api_config']
        working_config = ctx.obj['working_config']
        
        # Initialize API and calculator
        api = TogglAPI(api_config)
        calculator = TargetCalculator(working_config)
        
        # Show progress spinner
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            
            # Test internet connection
            task = progress.add_task("Checking internet connection...", total=None)
            try:
                import requests
                requests.get('https://www.google.com', timeout=5)
                progress.update(task, description=success_text("Internet connection OK"))
            except requests.RequestException:
                console.print(error_text("No internet connection!"))
                sys.exit(1)
            
            # Test API connection
            task = progress.add_task("Connecting to Toggl API...", total=None)
            if not api.test_connection():
                console.print(error_text("Failed to connect to Toggl API!"))
                sys.exit(1)
            progress.update(task, description=success_text("Toggl API connection OK"))
            
            # Fetch time data
            task = progress.add_task("Fetching time entries...", total=None)
            achieved_hours = api.get_hours_tracked(
                start_date=calculator.month_start,
                end_date=calculator.now
            )
            progress.update(task, description=f"Fetched {achieved_hours:.2f} hours")
        
        # Calculate targets
        target, min_hours, req_hours = calculator.get_daily_targets(achieved_hours)
        
        # Format and display status
        formatter = StatusFormatter(console)
        formatter.display_status(
            target=target,
            calculator=calculator,
            min_hours=min_hours,
            req_hours=req_hours
        )
        
    except TogglAPIError as e:
        console.print(error_text(f"Toggl API error: {e}"))
        sys.exit(1)
    except Exception as e:
        console.print(error_text(f"Unexpected error: {e}"))
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--format', 'output_format', 
              type=click.Choice(['table', 'json', 'yaml']), 
              default='table',
              help='Output format')
@click.pass_context
def report(ctx: click.Context, output_format: str):
    """Generate detailed report."""
    try:
        api_config = ctx.obj['api_config']
        working_config = ctx.obj['working_config']
        
        # Initialize API and calculator
        api = TogglAPI(api_config)
        calculator = TargetCalculator(working_config)
        
        # Fetch data
        achieved_hours = api.get_hours_tracked(
            start_date=calculator.month_start,
            end_date=calculator.now
        )
        
        # Calculate targets
        target, min_hours, req_hours = calculator.get_daily_targets(achieved_hours)
        
        # Generate report
        formatter = ReportFormatter(console)
        formatter.display_report(
            target=target,
            calculator=calculator,
            min_hours=min_hours,
            req_hours=req_hours,
            output_format=output_format
        )
        
    except TogglAPIError as e:
        console.print(error_text(f"Toggl API error: {e}"))
        sys.exit(1)
    except Exception as e:
        console.print(error_text(f"Unexpected error: {e}"))
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(), default='toggl-target.yaml')
@click.option('--force', is_flag=True, help='Overwrite existing file')
def init(path: str, force: bool):
    """Initialize configuration file."""
    config_path = Path(path)
    
    if config_path.exists() and not force:
        console.print(error_text(f"Configuration file {config_path} already exists. Use --force to overwrite."))
        sys.exit(1)
    
    try:
        config_manager = ConfigManager()
        config_manager.create_default_config(config_path)
        console.print(success_text(f"Created configuration file: {config_path}"))
        console.print(info_text("Edit the file to add your Toggl API token and customize settings."))
        
    except ConfigError as e:
        console.print(error_text(f"Failed to create config: {e}"))
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    console.print(f"toggl-target version 2.0.0")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()