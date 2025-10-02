"""
PocketJournal - A Windows-first personal journaling application.

Built with PySide6 for a native Windows experience.
"""

from .app_meta import VERSION, APP_NAME, ORG_NAME
from .main import main

__version__ = VERSION
__author__ = ORG_NAME
__email__ = "contact@myceliainteractive.com"

__all__ = ["main", "__version__"]