"""Date and time utilities."""

from datetime import datetime, timedelta
from typing import Optional

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR, SA, SU

from toggl_target.core.models import Weekday


def get_month_start(date: Optional[datetime] = None) -> datetime:
    """Get start of month for given date (or current date)."""
    if date is None:
        date = datetime.now()
    return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_month_end(date: Optional[datetime] = None) -> datetime:
    """Get end of month for given date (or current date)."""
    if date is None:
        date = datetime.now()
    # Go to first day of next month, then subtract 1 second
    next_month = date.replace(day=1) + relativedelta(months=1)
    return next_month - relativedelta(seconds=1)


def count_days_in_range(start_date: datetime, end_date: datetime, weekdays: Optional[list[Weekday]] = None) -> int:
    """Count days in date range, optionally filtered by weekdays.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        weekdays: List of weekdays to count, None for all days
    
    Returns:
        Number of days matching criteria
    """
    if weekdays:
        # Convert weekdays to rrule format
        weekday_map = {
            Weekday.MONDAY: MO,
            Weekday.TUESDAY: TU,
            Weekday.WEDNESDAY: WE,
            Weekday.THURSDAY: TH,
            Weekday.FRIDAY: FR,
            Weekday.SATURDAY: SA,
            Weekday.SUNDAY: SU,
        }
        byweekday = [weekday_map[day] for day in weekdays]
        count = rrule(DAILY, dtstart=start_date, until=end_date, byweekday=byweekday).count()
        return int(count) if count is not None else 0
    else:
        count = rrule(DAILY, dtstart=start_date, until=end_date).count()
        return int(count) if count is not None else 0


def get_business_days_remaining(from_date: Optional[datetime] = None, business_days: Optional[list[Weekday]] = None) -> int:
    """Get number of business days remaining in current month."""
    if from_date is None:
        from_date = datetime.now()
    
    month_end = get_month_end(from_date)
    
    if business_days is None:
        # Default to Monday-Friday
        business_days = [Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY, Weekday.THURSDAY, Weekday.FRIDAY]
    
    return count_days_in_range(from_date, month_end, business_days)


def get_total_days_remaining(from_date: Optional[datetime] = None) -> int:
    """Get total number of days remaining in current month."""
    if from_date is None:
        from_date = datetime.now()
    
    month_end = get_month_end(from_date)
    return count_days_in_range(from_date, month_end)


def get_business_days_elapsed(from_date: Optional[datetime] = None, business_days: Optional[list[Weekday]] = None) -> int:
    """Get number of business days that have elapsed in current month."""
    if from_date is None:
        from_date = datetime.now()
    
    month_start = get_month_start(from_date)
    
    if business_days is None:
        # Default to Monday-Friday
        business_days = [Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY, Weekday.THURSDAY, Weekday.FRIDAY]
    
    return count_days_in_range(month_start, from_date, business_days)


def get_total_days_elapsed(from_date: Optional[datetime] = None) -> int:
    """Get total number of days that have elapsed in current month."""
    if from_date is None:
        from_date = datetime.now()
    
    month_start = get_month_start(from_date)
    return count_days_in_range(month_start, from_date)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime from string."""
    return datetime.strptime(dt_str, format_str)


def is_same_month(date1: datetime, date2: datetime) -> bool:
    """Check if two dates are in the same month and year."""
    return date1.year == date2.year and date1.month == date2.month


def add_months(dt: datetime, months: int) -> datetime:
    """Add months to a date."""
    return dt + relativedelta(months=months)


def get_month_name(date: Optional[datetime] = None) -> str:
    """Get month name for given date (or current date)."""
    if date is None:
        date = datetime.now()
    return date.strftime("%B")


def get_year_month(date: Optional[datetime] = None) -> str:
    """Get year-month string for given date (or current date)."""
    if date is None:
        date = datetime.now()
    return date.strftime("%Y-%m")