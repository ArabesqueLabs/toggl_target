"""Utility functions for Toggl Target."""

from toggl_target.utils.terminal import (
    get_terminal_size,
    create_progress_bar,
    truncate_string,
    format_duration,
    format_number,
    colorize_text,
    success_text,
    error_text,
    warning_text,
    info_text,
)
from toggl_target.utils.date_utils import (
    get_month_start,
    get_month_end,
    count_days_in_range,
    get_business_days_remaining,
    get_total_days_remaining,
    get_business_days_elapsed,
    get_total_days_elapsed,
    format_datetime,
    parse_datetime,
    is_same_month,
    add_months,
    get_month_name,
    get_year_month,
)

__all__ = [
    # Terminal utilities
    "get_terminal_size",
    "create_progress_bar", 
    "truncate_string",
    "format_duration",
    "format_number",
    "colorize_text",
    "success_text",
    "error_text",
    "warning_text",
    "info_text",
    # Date utilities
    "get_month_start",
    "get_month_end",
    "count_days_in_range",
    "get_business_days_remaining",
    "get_total_days_remaining",
    "get_business_days_elapsed",
    "get_total_days_elapsed",
    "format_datetime",
    "parse_datetime",
    "is_same_month",
    "add_months",
    "get_month_name",
    "get_year_month",
]