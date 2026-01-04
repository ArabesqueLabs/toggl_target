"""Core data models for Toggl Target."""

from datetime import datetime
from typing import List, Optional
from enum import IntEnum

from dateutil.rrule import SA, SU, MO, TU, WE, TH, FR
from pydantic import BaseModel, Field, validator


class Weekday(IntEnum):
    """Enumeration for weekdays."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class WorkingTimeConfig(BaseModel):
    """Configuration for working time calculations."""
    
    working_hours_per_day: float = Field(default=8.0, ge=0, le=24, description="Hours to work per business day")
    business_days: List[Weekday] = Field(
        default=[Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY, Weekday.THURSDAY, Weekday.FRIDAY],
        description="Days considered as business days"
    )
    tolerance_percentage: float = Field(default=0.1, ge=0, le=1, description="Tolerance for target achievement")
    
    @validator('business_days')
    def validate_business_days(cls, v):
        if not v:
            raise ValueError('At least one business day must be specified')
        return v
    
    @property
    def business_days_rrule(self) -> List:
        """Convert business days to rrule format."""
        mapping = {
            Weekday.MONDAY: MO,
            Weekday.TUESDAY: TU,
            Weekday.WEDNESDAY: WE,
            Weekday.THURSDAY: TH,
            Weekday.FRIDAY: FR,
            Weekday.SATURDAY: SA,
            Weekday.SUNDAY: SU,
        }
        return [mapping[day] for day in self.business_days]


class Target(BaseModel):
    """Target achievement data."""
    
    achieved_hours: float = Field(default=0.0, ge=0, description="Hours already tracked")
    required_hours: float = Field(gt=0, description="Total hours required for the period")
    tolerance: float = Field(default=0.1, ge=0, le=1, description="Tolerance percentage")
    
    @property
    def minimum_hours(self) -> float:
        """Minimum hours to achieve considering tolerance."""
        return self.required_hours - (self.tolerance * self.required_hours)
    
    @property
    def left_to_minimum(self) -> float:
        """Hours left to reach minimum target."""
        return max(self.minimum_hours - self.achieved_hours, 0)
    
    @property
    def left_to_required(self) -> float:
        """Hours left to reach required target."""
        return max(self.required_hours - self.achieved_hours, 0)
    
    @property
    def achieved_percentage(self) -> float:
        """Percentage of required hours achieved."""
        if self.required_hours == 0:
            return 0.0
        return self.achieved_hours / self.required_hours
    
    def get_required_daily_hours(self, business_days: int, total_days: int) -> tuple[float, float]:
        """Calculate required daily hours for business days and all days."""
        normal_hours = self.left_to_required / max(business_days, 1)
        crunch_hours = self.left_to_required / max(total_days, 1)
        return normal_hours, crunch_hours
    
    def get_minimum_daily_hours(self, business_days: int, total_days: int) -> tuple[float, float]:
        """Calculate minimum daily hours for business days and all days."""
        normal_hours = self.left_to_minimum / max(business_days, 1)
        crunch_hours = self.left_to_minimum / max(total_days, 1)
        return normal_hours, crunch_hours


class TimeEntry(BaseModel):
    """Represents a Toggl time entry."""
    
    id: int
    description: Optional[str] = None
    duration: int  # Duration in seconds, negative means currently running
    start: datetime
    stop: Optional[datetime] = None
    project_id: Optional[int] = None
    workspace_id: int
    
    @property
    def is_running(self) -> bool:
        """Check if the time entry is currently running."""
        return self.duration < 0
    
    @property
    def hours(self) -> float:
        """Get duration in hours."""
        if self.is_running:
            return 0.0  # Don't count running entries
        return abs(self.duration) / 3600.0


class APIConfig(BaseModel):
    """Configuration for Toggl API."""
    
    api_token: str = Field(min_length=1, description="Toggl API token")
    timezone: str = Field(default="+00:00", description="Timezone for API requests")
    base_url: str = Field(default="https://www.toggl.com/api/v8", description="Toggl API base URL")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")