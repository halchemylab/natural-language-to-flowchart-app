"""
This module initializes the UI components of the application, 
making them available for use in the main app file.
"""

from .sidebar import render_sidebar
from .main_panel import render_main_panel

__all__ = ["render_sidebar", "render_main_panel"]
