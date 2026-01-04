"""Toggl Target - Modern time tracking target calculator."""

__version__ = "2.0.0"
__author__ = "Mosab Ibrahim"
__email__ = "mosab.a.ibrahim@gmail.com"

from toggl_target.core.models import Target, WorkingTimeConfig
from toggl_target.core.calculator import TargetCalculator
from toggl_target.core.api import TogglAPI

__all__ = ["Target", "WorkingTimeConfig", "TargetCalculator", "TogglAPI"]