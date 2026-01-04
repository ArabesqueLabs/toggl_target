"""Toggl API client with modern error handling."""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode

import requests
from requests.auth import HTTPBasicAuth

from toggl_target.core.models import APIConfig, TimeEntry


logger = logging.getLogger(__name__)


class TogglAPIError(Exception):
    """Base exception for Toggl API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class TogglAPI:
    """Modern Toggl API client with proper error handling."""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(config.api_token, 'api_token')
        self.session.headers.update({'content-type': 'application/json'})
    
    def _make_url(self, section: str = 'time_entries', params: Optional[Dict[str, str]] = None) -> str:
        """Construct API URL with parameters."""
        url = f'{self.config.base_url}/{section}'
        if params:
            url = f'{url}?{urlencode(params)}'
        return url
    
    def _query(self, url: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Execute API request with error handling."""
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout as e:
            raise TogglAPIError(f"Request timeout after {self.config.timeout}s") from e
        except requests.exceptions.ConnectionError as e:
            raise TogglAPIError("Connection failed - check internet connection") from e
        except requests.exceptions.HTTPError as e:
            response = e.response
            status_code = response.status_code if response else None
            text = response.text if response else "Unknown error"
            raise TogglAPIError(
                f"HTTP {status_code}: {text}",
                status_code=status_code
            ) from e
        except requests.exceptions.RequestException as e:
            raise TogglAPIError(f"Request failed: {str(e)}") from e
    
    def get_time_entries(self, start_date: datetime, end_date: datetime) -> List[TimeEntry]:
        """Get time entries for a date range."""
        params = {
            'start_date': f"{start_date.isoformat()}{self.config.timezone}",
            'end_date': f"{end_date.isoformat()}{self.config.timezone}"
        }
        
        url = self._make_url('time_entries', params)
        response = self._query(url)
        
        try:
            data = response.json()
        except ValueError as e:
            raise TogglAPIError("Invalid JSON response") from e
        
        if not isinstance(data, list):
            raise TogglAPIError("Expected list of time entries")
        
        entries = []
        for entry_data in data:
            try:
                entry = self._parse_time_entry(entry_data)
                entries.append(entry)
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse time entry: {entry_data}, error: {e}")
                continue
        
        return entries
    
    def _parse_time_entry(self, data: Dict[str, Any]) -> TimeEntry:
        """Parse time entry from API response."""
        required_fields = ['id', 'duration', 'start', 'workspace_id']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Parse datetime
        try:
            start_time = datetime.fromisoformat(data['start'].replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid start time format: {data.get('start')}") from e
        
        # Parse optional stop time
        stop_time = None
        if data.get('stop'):
            try:
                stop_time = datetime.fromisoformat(data['stop'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                logger.warning(f"Invalid stop time format: {data.get('stop')}")
        
        return TimeEntry(
            id=int(data['id']),
            description=data.get('description'),
            duration=int(data['duration']),
            start=start_time,
            stop=stop_time,
            project_id=data.get('project_id'),
            workspace_id=int(data['workspace_id'])
        )
    
    def get_hours_tracked(self, start_date: datetime, end_date: datetime) -> float:
        """Get total hours tracked for a date range."""
        entries = self.get_time_entries(start_date, end_date)
        total_hours = sum(entry.hours for entry in entries)
        return total_hours
    
    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            # Try to get current user info
            url = self._make_url('me')
            response = self._query(url)
            return response.status_code == 200
        except TogglAPIError:
            return False
    
    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get available workspaces."""
        url = self._make_url('workspaces')
        response = self._query(url)
        return response.json()