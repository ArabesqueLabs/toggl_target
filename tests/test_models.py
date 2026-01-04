"""Test data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from toggl_target.core.models import Target, WorkingTimeConfig, APIConfig, Weekday


class TestTarget:
    """Test Target model."""
    
    def test_target_creation(self):
        """Test creating a valid target."""
        target = Target(
            achieved_hours=80.0,
            required_hours=160.0,
            tolerance=0.1
        )
        
        assert target.achieved_hours == 80.0
        assert target.required_hours == 160.0
        assert target.tolerance == 0.1
    
    def test_minimum_hours(self):
        """Test minimum hours calculation."""
        target = Target(
            achieved_hours=80.0,
            required_hours=160.0,
            tolerance=0.1
        )
        
        assert target.minimum_hours == 144.0  # 160 - (0.1 * 160)
    
    def test_left_to_minimum(self):
        """Test hours left to minimum."""
        target = Target(
            achieved_hours=140.0,
            required_hours=160.0,
            tolerance=0.1
        )
        
        assert target.left_to_minimum == 4.0  # 144 - 140
        
        # Test when already achieved minimum
        target.achieved_hours = 150.0
        assert target.left_to_minimum == 0.0
    
    def test_left_to_required(self):
        """Test hours left to required."""
        target = Target(
            achieved_hours=100.0,
            required_hours=160.0,
            tolerance=0.1
        )
        
        assert target.left_to_required == 60.0  # 160 - 100
        
        # Test when already achieved required
        target.achieved_hours = 180.0
        assert target.left_to_required == 0.0
    
    def test_achieved_percentage(self):
        """Test achieved percentage calculation."""
        target = Target(
            achieved_hours=80.0,
            required_hours=160.0,
            tolerance=0.1
        )
        
        assert target.achieved_percentage == 0.5  # 80 / 160
    
    def test_get_required_daily_hours(self):
        """Test daily required hours calculation."""
        target = Target(
            achieved_hours=80.0,
            required_hours=160.0,
            tolerance=0.1
        )
        
        normal, crunch = target.get_required_daily_hours(business_days=10, total_days=15)
        
        assert normal == 8.0  # 80 hours left / 10 business days
        assert crunch == 5.33  # 80 hours left / 15 total days (approximately)
    
    def test_get_minimum_daily_hours(self):
        """Test daily minimum hours calculation."""
        target = Target(
            achieved_hours=80.0,
            required_hours=160.0,
            tolerance=0.1
        )
        
        normal, crunch = target.get_minimum_daily_hours(business_days=10, total_days=15)
        
        assert normal == 6.4  # 64 hours left / 10 business days
        assert crunch == 4.27  # 64 hours left / 15 total days (approximately)


class TestWorkingTimeConfig:
    """Test WorkingTimeConfig model."""
    
    def test_default_config(self):
        """Test creating default configuration."""
        config = WorkingTimeConfig()
        
        assert config.working_hours_per_day == 8.0
        assert len(config.business_days) == 5  # Monday-Friday
        assert config.tolerance_percentage == 0.1
    
    def test_custom_config(self):
        """Test creating custom configuration."""
        config = WorkingTimeConfig(
            working_hours_per_day=7.5,
            business_days=[Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY],
            tolerance_percentage=0.2
        )
        
        assert config.working_hours_per_day == 7.5
        assert len(config.business_days) == 3
        assert config.tolerance_percentage == 0.2
    
    def test_validation_negative_hours(self):
        """Test validation of negative working hours."""
        with pytest.raises(ValidationError):
            WorkingTimeConfig(working_hours_per_day=-1.0)
    
    def test_validation_too_many_hours(self):
        """Test validation of too many working hours."""
        with pytest.raises(ValidationError):
            WorkingTimeConfig(working_hours_per_day=25.0)
    
    def test_validation_empty_business_days(self):
        """Test validation of empty business days."""
        with pytest.raises(ValidationError):
            WorkingTimeConfig(business_days=[])
    
    def test_validation_tolerance_too_high(self):
        """Test validation of tolerance percentage too high."""
        with pytest.raises(ValidationError):
            WorkingTimeConfig(tolerance_percentage=1.5)
    
    def test_business_days_rrule(self):
        """Test conversion to rrule format."""
        config = WorkingTimeConfig(
            business_days=[Weekday.MONDAY, Weekday.WEDNESDAY, Weekday.FRIDAY]
        )
        
        rrule_days = config.business_days_rrule
        assert len(rrule_days) == 3


class TestAPIConfig:
    """Test APIConfig model."""
    
    def test_default_config(self):
        """Test creating default API configuration."""
        config = APIConfig(api_token="test_token")
        
        assert config.api_token == "test_token"
        assert config.timezone == "+00:00"
        assert config.base_url == "https://www.toggl.com/api/v8"
        assert config.timeout == 30
    
    def test_custom_config(self):
        """Test creating custom API configuration."""
        config = APIConfig(
            api_token="custom_token",
            timezone="+02:00",
            base_url="https://custom.toggl.com/api",
            timeout=60
        )
        
        assert config.api_token == "custom_token"
        assert config.timezone == "+02:00"
        assert config.base_url == "https://custom.toggl.com/api"
        assert config.timeout == 60
    
    def test_validation_empty_token(self):
        """Test validation of empty API token."""
        with pytest.raises(ValidationError):
            APIConfig(api_token="")
    
    def test_validation_invalid_timeout(self):
        """Test validation of invalid timeout."""
        with pytest.raises(ValidationError):
            APIConfig(api_token="test", timeout=0)
        
        with pytest.raises(ValidationError):
            APIConfig(api_token="test", timeout=400)