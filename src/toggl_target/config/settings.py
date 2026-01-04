"""Configuration management for Toggl Target."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import yaml
from pydantic import ValidationError

from toggl_target.core.models import WorkingTimeConfig, APIConfig, Weekday


logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration related errors."""
    pass


class ConfigManager:
    """Manages application configuration from files and environment."""
    
    DEFAULT_CONFIG_PATHS = [
        Path.cwd() / "toggl-target.yaml",
        Path.cwd() / "toggl-target.yml", 
        Path.cwd() / ".toggl-target.yaml",
        Path.home() / ".config" / "toggl-target" / "config.yaml",
        Path.home() / ".toggl-target.yaml",
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self._working_config: Optional[WorkingTimeConfig] = None
        self._api_config: Optional[APIConfig] = None
    
    def load_config(self) -> tuple[WorkingTimeConfig, APIConfig]:
        """Load configuration from file and environment variables."""
        config_data = self._load_config_file()
        config_data.update(self._load_env_config())
        
        # Validate and create configs
        try:
            working_config = self._create_working_config(config_data)
            api_config = self._create_api_config(config_data)
            
            self._working_config = working_config
            self._api_config = api_config
            
            return working_config, api_config
            
        except ValidationError as e:
            raise ConfigError(f"Configuration validation failed: {e}")
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_path and self.config_path.exists():
            config_file = self.config_path
        else:
            config_file = self._find_config_file()
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ConfigError(f"Invalid YAML in config file {config_file}: {e}")
            except IOError as e:
                raise ConfigError(f"Could not read config file {config_file}: {e}")
        
        return {}
    
    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file in default locations."""
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                return path
        return None
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        
        # API configuration
        if os.getenv('TOGGL_API_TOKEN'):
            env_config['api_token'] = os.getenv('TOGGL_API_TOKEN')
        
        if os.getenv('TOGGL_TIMEZONE'):
            env_config['timezone'] = os.getenv('TOGGL_TIMEZONE')
        
        # Working time configuration
        hours_env = os.getenv('WORKING_HOURS_PER_DAY')
        if hours_env:
            try:
                env_config['working_hours_per_day'] = float(hours_env)
            except ValueError:
                logger.warning("Invalid WORKING_HOURS_PER_DAY environment variable")
        
        tolerance_env = os.getenv('TOLERANCE_PERCENTAGE')
        if tolerance_env:
            try:
                env_config['tolerance_percentage'] = float(tolerance_env)
            except ValueError:
                logger.warning("Invalid TOLERANCE_PERCENTAGE environment variable")
        
        # Business days
        days_env = os.getenv('BUSINESS_DAYS')
        if days_env:
            days_str = days_env.upper()
            day_mapping = {
                'MON': Weekday.MONDAY,
                'TUE': Weekday.TUESDAY, 
                'WED': Weekday.WEDNESDAY,
                'THU': Weekday.THURSDAY,
                'FRI': Weekday.FRIDAY,
                'SAT': Weekday.SATURDAY,
                'SUN': Weekday.SUNDAY,
            }
            
            days = []
            for day_name in days_str.split(','):
                day_name = day_name.strip()
                if day_name in day_mapping:
                    days.append(day_mapping[day_name])
            
            if days:
                env_config['business_days'] = days
        
        return env_config
    
    def _create_working_config(self, config_data: Dict[str, Any]) -> WorkingTimeConfig:
        """Create working time configuration from data."""
        working_data = config_data.get('working_time', {})
        
        # Handle legacy format
        if 'working_hours_per_day' not in working_data:
            working_data['working_hours_per_day'] = config_data.get('working_hours_per_day', 8.0)
        
        if 'tolerance_percentage' not in working_data:
            working_data['tolerance_percentage'] = config_data.get('tolerance_percentage', 0.1)
        
        if 'business_days' not in working_data:
            # Default to Monday-Friday
            working_data['business_days'] = [
                Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY, 
                Weekday.THURSDAY, Weekday.FRIDAY
            ]
        
        return WorkingTimeConfig(**working_data)
    
    def _create_api_config(self, config_data: Dict[str, Any]) -> APIConfig:
        """Create API configuration from data."""
        api_data = config_data.get('api', {})
        
        # Handle legacy format
        if 'api_token' not in api_data:
            api_data['api_token'] = config_data.get('api_token', '')
        
        if 'timezone' not in api_data:
            api_data['timezone'] = config_data.get('timezone', '+00:00')
        
        if not api_data.get('api_token'):
            raise ConfigError("API token is required. Set TOGGL_API_TOKEN environment variable or configure in config file.")
        
        return APIConfig(**api_data)
    
    def create_default_config(self, path: Path) -> None:
        """Create a default configuration file."""
        default_config = {
            'api': {
                'api_token': 'YOUR_TOGGL_API_TOKEN_HERE',
                'timezone': '+00:00',
                'timeout': 30
            },
            'working_time': {
                'working_hours_per_day': 8.0,
                'business_days': ['MON', 'TUE', 'WED', 'THU', 'FRI'],
                'tolerance_percentage': 0.1
            }
        }
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Created default config at {path}")
            
        except IOError as e:
            raise ConfigError(f"Could not create config file {path}: {e}")
    
    @property
    def working_config(self) -> WorkingTimeConfig:
        """Get working time configuration."""
        if self._working_config is None:
            raise ConfigError("Configuration not loaded. Call load_config() first.")
        return self._working_config
    
    @property
    def api_config(self) -> APIConfig:
        """Get API configuration."""
        if self._api_config is None:
            raise ConfigError("Configuration not loaded. Call load_config() first.")
        return self._api_config