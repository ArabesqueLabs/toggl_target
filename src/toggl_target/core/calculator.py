"""Target calculator for working time and progress."""

from datetime import datetime
from typing import Tuple

from dateutil.rrule import rrule, DAILY
from dateutil.relativedelta import relativedelta

from toggl_target.core.models import WorkingTimeConfig, Target


class TargetCalculator:
    """Calculator for working time and target progress."""
    
    def __init__(self, config: WorkingTimeConfig):
        self.config = config
        self._now = None
    
    @property
    def now(self) -> datetime:
        """Current time, can be overridden for testing."""
        if self._now is None:
            return datetime.now().replace(microsecond=0)
        return self._now
    
    def set_time(self, dt: datetime) -> None:
        """Set the current time for testing purposes."""
        self._now = dt.replace(microsecond=0)
    
    @property
    def month_start(self) -> datetime:
        """Start of the current month."""
        return self.now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @property
    def month_end(self) -> datetime:
        """End of the current month."""
        return self.now.replace(day=1) + relativedelta(months=1, days=-1, hour=23, minute=59, second=59, microsecond=0)
    
    @property
    def total_business_days_count(self) -> int:
        """Total number of business days in the current month."""
        count = rrule(
            DAILY, 
            dtstart=self.month_start, 
            until=self.month_end, 
            byweekday=self.config.business_days_rrule
        ).count()
        return int(count) if count is not None else 0
    
    @property
    def total_days_count(self) -> int:
        """Total number of days in the current month."""
        count = rrule(
            DAILY, 
            dtstart=self.month_start, 
            until=self.month_end
        ).count()
        return int(count) if count is not None else 0
    
    @property
    def business_days_left_count(self) -> int:
        """Number of business days remaining in the current month."""
        count = rrule(
            DAILY, 
            dtstart=self.now, 
            until=self.month_end, 
            byweekday=self.config.business_days_rrule
        ).count()
        return int(count) if count is not None else 0
    
    @property
    def days_left_count(self) -> int:
        """Number of days remaining in the current month."""
        count = rrule(
            DAILY, 
            dtstart=self.now, 
            until=self.month_end
        ).count()
        return int(count) if count is not None else 0
    
    @property
    def business_days_elapsed_count(self) -> int:
        """Number of business days that have passed in the current month."""
        count = rrule(
            DAILY, 
            dtstart=self.month_start, 
            until=self.now, 
            byweekday=self.config.business_days_rrule
        ).count()
        return int(count) if count is not None else 0
    
    @property
    def days_elapsed_count(self) -> int:
        """Number of days that have passed in the current month."""
        count = rrule(
            DAILY, 
            dtstart=self.month_start, 
            until=self.now
        ).count()
        return int(count) if count is not None else 0
    
    @property
    def required_hours_this_month(self) -> float:
        """Total required hours for the current month."""
        return self.total_business_days_count * self.config.working_hours_per_day
    
    def create_target(self, achieved_hours: float) -> Target:
        """Create a Target instance with current month data."""
        return Target(
            achieved_hours=achieved_hours,
            required_hours=self.required_hours_this_month,
            tolerance=self.config.tolerance_percentage
        )
    
    def get_daily_targets(self, achieved_hours: float) -> Tuple[Target, Tuple[float, float], Tuple[float, float]]:
        """Get comprehensive daily target information.
        
        Returns:
            Tuple containing:
            - Target instance
            - (normal_min_hours, crunch_min_hours) for minimum targets
            - (normal_req_hours, crunch_req_hours) for required targets
        """
        target = self.create_target(achieved_hours)
        min_hours = target.get_minimum_daily_hours(self.business_days_left_count, self.days_left_count)
        req_hours = target.get_required_daily_hours(self.business_days_left_count, self.days_left_count)
        
        return target, min_hours, req_hours