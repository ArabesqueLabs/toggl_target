"""Test configuration and fixtures."""

import pytest
from datetime import datetime
from pathlib import Path

from toggl_target.core.models import WorkingTimeConfig, APIConfig, Target, Weekday
from toggl_target.core.calculator import TargetCalculator


@pytest.fixture
def working_config():
    """Default working time configuration."""
    return WorkingTimeConfig(
        working_hours_per_day=8.0,
        business_days=[Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY, Weekday.THURSDAY, Weekday.FRIDAY],
        tolerance_percentage=0.1
    )


@pytest.fixture
def api_config():
    """Default API configuration."""
    return APIConfig(
        api_token="test_token_123",
        timezone="+00:00"
    )


@pytest.fixture
def target():
    """Default target for testing."""
    return Target(
        achieved_hours=80.0,
        required_hours=160.0,
        tolerance=0.1
    )


@pytest.fixture
def calculator(working_config):
    """Calculator with default configuration."""
    return TargetCalculator(working_config)


@pytest.fixture
def sample_time_entries():
    """Sample time entries for testing."""
    from toggl_target.core.models import TimeEntry
    
    return [
        TimeEntry(
            id=1,
            description="Task 1",
            duration=8 * 3600,  # 8 hours
            start=datetime(2024, 1, 1, 9, 0, 0),
            stop=datetime(2024, 1, 1, 17, 0, 0),
            workspace_id=12345
        ),
        TimeEntry(
            id=2,
            description="Task 2",
            duration=4 * 3600,  # 4 hours
            start=datetime(2024, 1, 2, 9, 0, 0),
            stop=datetime(2024, 1, 2, 13, 0, 0),
            workspace_id=12345
        ),
        TimeEntry(
            id=3,
            description="Running task",
            duration=-1,  # Currently running
            start=datetime(2024, 1, 3, 9, 0, 0),
            workspace_id=12345
        )
    ]


@pytest.fixture
def mock_date():
    """Mock date for testing (middle of month)."""
    return datetime(2024, 1, 15, 12, 0, 0)