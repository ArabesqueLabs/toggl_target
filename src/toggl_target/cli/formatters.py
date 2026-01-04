"""Output formatters for CLI."""

import json
from datetime import datetime
from typing import Optional

import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn

from toggl_target.core import TargetCalculator, Target
from toggl_target.utils import (
    create_progress_bar,
    success_text,
    error_text,
    warning_text,
    info_text,
    format_duration,
    format_number,
    get_month_name,
    get_year_month,
)


class StatusFormatter:
    """Formatter for status command output."""
    
    def __init__(self, console: Console):
        self.console = console
    
    def display_status(
        self,
        target: Target,
        calculator: TargetCalculator,
        min_hours: tuple[float, float],
        req_hours: tuple[float, float]
    ) -> None:
        """Display current status in terminal."""
        # Header
        self.console.print(Panel(
            f"[bold blue]Toggl Target Status[/bold blue]\n"
            f"[dim]{get_month_name()} {datetime.now().year}[/dim]",
            border_style="blue"
        ))
        
        # Hours tracked
        hours_color = "green" if target.achieved_hours > 0 else "yellow"
        self.console.print(f"\n📊 Hours tracked: [{hours_color} bold]{format_duration(target.achieved_hours)}[/{hours_color} bold]")
        
        # Time remaining
        self.console.print(f"\n📅 Business days remaining: [cyan]{calculator.business_days_left_count}[/cyan]")
        self.console.print(f"📅 Total days remaining: [cyan]{calculator.days_left_count}[/cyan]")
        
        # Targets
        self.console.print(f"\n🎯 Monthly targets:")
        self.console.print(f"   Required: [bold]{format_duration(target.required_hours)}[/bold]")
        self.console.print(f"   Minimum ({target.tolerance*100:.0f}% tolerance): [dim]{format_duration(target.minimum_hours)}[/dim]")
        
        # Daily requirements for minimum
        normal_min, crunch_min = min_hours
        self.console.print(f"\n📈 To achieve [green]minimum[/green] target:")
        self.console.print(f"   Business days: [yellow]{format_number(normal_min)}h/day[/yellow]")
        self.console.print(f"   All days: [yellow]{format_number(crunch_min)}h/day[/yellow]")
        self.console.print(f"   Hours left: [dim]{format_duration(target.left_to_minimum)}[/dim]")
        
        # Daily requirements for required
        normal_req, crunch_req = req_hours
        self.console.print(f"\n📈 To achieve [red]required[/red] target:")
        self.console.print(f"   Business days: [orange_red1]{format_number(normal_req)}h/day[/orange_red1]")
        self.console.print(f"   All days: [orange_red1]{format_number(crunch_req)}h/day[/orange_red1]")
        self.console.print(f"   Hours left: [dim]{format_duration(target.left_to_required)}[/dim]")
        
        # Progress bar
        progress_text = create_progress_bar(
            target.achieved_percentage,
            tolerance=target.tolerance
        )
        self.console.print(f"\n{progress_text}")
        
        # Status indicator
        if target.achieved_percentage >= 1.0:
            self.console.print(f"\n✅ {success_text('Target achieved!')}")
        elif target.achieved_percentage >= (1.0 - target.tolerance):
            self.console.print(f"\n⚠️  {warning_text('Almost there - within tolerance!')}")
        else:
            percentage_left = (1.0 - target.achieved_percentage) * 100
            self.console.print(f"\n📊 {info_text(f'{percentage_left:.1f}% remaining to target')}")


class ReportFormatter:
    """Formatter for report command output."""
    
    def __init__(self, console: Console):
        self.console = console
    
    def display_report(
        self,
        target: Target,
        calculator: TargetCalculator,
        min_hours: tuple[float, float],
        req_hours: tuple[float, float],
        output_format: str = 'table'
    ) -> None:
        """Display detailed report."""
        if output_format == 'table':
            self._display_table(target, calculator, min_hours, req_hours)
        elif output_format == 'json':
            self._display_json(target, calculator, min_hours, req_hours)
        elif output_format == 'yaml':
            self._display_yaml(target, calculator, min_hours, req_hours)
    
    def _display_table(
        self,
        target: Target,
        calculator: TargetCalculator,
        min_hours: tuple[float, float],
        req_hours: tuple[float, float]
    ) -> None:
        """Display report as table."""
        # Overview table
        overview_table = Table(title="Monthly Overview", show_header=True, header_style="bold blue")
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="white")
        
        overview_table.add_row("Period", f"{get_year_month()}")
        overview_table.add_row("Hours Achieved", format_duration(target.achieved_hours))
        overview_table.add_row("Hours Required", format_duration(target.required_hours))
        overview_table.add_row("Hours to Minimum", format_duration(target.left_to_minimum))
        overview_table.add_row("Hours to Required", format_duration(target.left_to_required))
        overview_table.add_row("Progress", f"{target.achieved_percentage*100:.1f}%")
        
        self.console.print(overview_table)
        
        # Days remaining table
        days_table = Table(title="Days Remaining", show_header=True, header_style="bold blue")
        days_table.add_column("Type", style="cyan")
        days_table.add_column("Count", style="white")
        
        days_table.add_row("Business Days", str(calculator.business_days_left_count))
        days_table.add_row("All Days", str(calculator.days_left_count))
        days_table.add_row("Business Days Elapsed", str(calculator.business_days_elapsed_count))
        days_table.add_row("All Days Elapsed", str(calculator.days_elapsed_count))
        
        self.console.print(days_table)
        
        # Daily targets table
        daily_table = Table(title="Daily Targets", show_header=True, header_style="bold blue")
        daily_table.add_column("Target Type", style="cyan")
        daily_table.add_column("Business Days", style="white")
        daily_table.add_column("All Days", style="white")
        
        normal_min, crunch_min = min_hours
        normal_req, crunch_req = req_hours
        
        daily_table.add_row("Minimum", f"{format_number(normal_min)}h", f"{format_number(crunch_min)}h")
        daily_table.add_row("Required", f"{format_number(normal_req)}h", f"{format_number(crunch_req)}h")
        
        self.console.print(daily_table)
    
    def _display_json(
        self,
        target: Target,
        calculator: TargetCalculator,
        min_hours: tuple[float, float],
        req_hours: tuple[float, float]
    ) -> None:
        """Display report as JSON."""
        data = self._create_report_data(target, calculator, min_hours, req_hours)
        json_output = json.dumps(data, indent=2, default=str)
        self.console.print(json_output)
    
    def _display_yaml(
        self,
        target: Target,
        calculator: TargetCalculator,
        min_hours: tuple[float, float],
        req_hours: tuple[float, float]
    ) -> None:
        """Display report as YAML."""
        data = self._create_report_data(target, calculator, min_hours, req_hours)
        yaml_output = yaml.dump(data, indent=2, sort_keys=False)
        self.console.print(yaml_output)
    
    def _create_report_data(
        self,
        target: Target,
        calculator: TargetCalculator,
        min_hours: tuple[float, float],
        req_hours: tuple[float, float]
    ) -> dict:
        """Create dictionary data for report."""
        normal_min, crunch_min = min_hours
        normal_req, crunch_req = req_hours
        
        return {
            "period": {
                "year": datetime.now().year,
                "month": datetime.now().month,
                "month_name": get_month_name(),
                "year_month": get_year_month()
            },
            "targets": {
                "achieved_hours": target.achieved_hours,
                "required_hours": target.required_hours,
                "minimum_hours": target.minimum_hours,
                "left_to_minimum": target.left_to_minimum,
                "left_to_required": target.left_to_required,
                "achieved_percentage": round(target.achieved_percentage * 100, 2),
                "tolerance_percentage": round(target.tolerance * 100, 2)
            },
            "days": {
                "business_days_total": calculator.total_business_days_count,
                "total_days": calculator.total_days_count,
                "business_days_remaining": calculator.business_days_left_count,
                "total_days_remaining": calculator.days_left_count,
                "business_days_elapsed": calculator.business_days_elapsed_count,
                "total_days_elapsed": calculator.days_elapsed_count
            },
            "daily_targets": {
                "minimum": {
                    "business_days": round(normal_min, 2),
                    "all_days": round(crunch_min, 2)
                },
                "required": {
                    "business_days": round(normal_req, 2),
                    "all_days": round(crunch_req, 2)
                }
            },
            "generated_at": datetime.now().isoformat()
        }