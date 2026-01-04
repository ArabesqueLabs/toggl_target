"""Terminal utilities for modern CLI output."""

import os
import shutil
from typing import Optional, Tuple


def get_terminal_size() -> Tuple[int, int]:
    """Get terminal size (width, height)."""
    try:
        return shutil.get_terminal_size()
    except (OSError, AttributeError):
        # Fallback to environment variables or defaults
        width = os.environ.get('COLUMNS', '80')
        height = os.environ.get('LINES', '25')
        return int(width), int(height)


def create_progress_bar(percentage: float, width: Optional[int] = None, tolerance: float = 0.0) -> str:
    """Create a progress bar string.
    
    Args:
        percentage: Progress percentage (0.0 to 1.0)
        width: Bar width in characters, defaults to terminal width
        tolerance: Tolerance position (0.0 to 1.0), shows a marker
    
    Returns:
        Progress bar string
    """
    if width is None:
        terminal_width, _ = get_terminal_size()
        width = max(terminal_width - 10, 20)  # Leave space for percentage
    
    # Calculate bar components
    filled_chars = int(percentage * width)
    empty_chars = width - filled_chars
    
    # Create bar
    bar = "█" * filled_chars + "░" * empty_chars
    
    # Add tolerance marker if specified
    if tolerance > 0 and tolerance < 1.0:
        marker_pos = int(tolerance * width)
        if marker_pos < len(bar):
            bar = bar[:marker_pos] + "│" + bar[marker_pos + 1:]
    
    # Format with percentage
    percentage_str = f"{percentage * 100:5.1f}%"
    return f"{percentage_str} [{bar}]"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_duration(hours: float, precision: int = 2) -> str:
    """Format hours in human readable format."""
    if hours < 1.0:
        minutes = int(hours * 60)
        return f"{minutes}m"
    else:
        return f"{hours:.{precision}f}h"


def format_number(number: float, precision: int = 2) -> str:
    """Format number with specified precision."""
    return f"{number:.{precision}f}"


def colorize_text(text: str, color: str, bold: bool = False) -> str:
    """Add ANSI color codes to text.
    
    Args:
        text: Text to colorize
        color: Color name (red, green, yellow, blue, magenta, cyan, white)
        bold: Whether to make text bold
    
    Returns:
        Colorized text with ANSI codes
    """
    colors = {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37',
        'reset': '0'
    }
    
    color_code = colors.get(color.lower(), colors['white'])
    codes = [color_code]
    
    if bold:
        codes.append('1')
    
    return f"\x1b[{' '.join(codes)}m{text}\x1b[0m"


def success_text(text: str) -> str:
    """Return text in green (success)."""
    return colorize_text(text, 'green', bold=True)


def error_text(text: str) -> str:
    """Return text in red (error)."""
    return colorize_text(text, 'red', bold=True)


def warning_text(text: str) -> str:
    """Return text in yellow (warning)."""
    return colorize_text(text, 'yellow', bold=True)


def info_text(text: str) -> str:
    """Return text in blue (info)."""
    return colorize_text(text, 'blue', bold=True)