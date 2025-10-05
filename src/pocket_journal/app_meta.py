"""
Application metadata and constants for PocketJournal.

This module defines core application constants including name, organization,
and version information read from version.json.
"""

import json
from pathlib import Path
from typing import Dict, Any

# Core application constants
APP_NAME = "PocketJournal"
ORG_NAME = "DigiArtifact"

# Path to version file
_VERSION_FILE = Path(__file__).parent.parent.parent / "version.json"


def _load_version_info() -> Dict[str, Any]:
    """Load version information from version.json file."""
    try:
        with open(_VERSION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        # Fallback version info if file is missing or corrupted
        return {
            "version": "0.1.0",
            "build_date": "unknown",
            "channel": "dev"
        }


# Load version information
_version_info = _load_version_info()

# Export version constants
VERSION = _version_info["version"]
BUILD_DATE = _version_info["build_date"]
CHANNEL = _version_info["channel"]

# Application display information
APP_DISPLAY_NAME = f"{APP_NAME} v{VERSION}"
APP_FULL_NAME = f"{ORG_NAME} {APP_NAME}"

# Channel-specific information
IS_DEV_CHANNEL = CHANNEL == "dev"
IS_BETA_CHANNEL = CHANNEL == "beta"
IS_RELEASE_CHANNEL = CHANNEL == "release"

# Application URLs and identifiers
APP_IDENTIFIER = f"com.{ORG_NAME.lower().replace(' ', '')}.{APP_NAME.lower()}"
GITHUB_URL = "https://github.com/yourusername/pocket-journal"
SUPPORT_URL = "https://github.com/yourusername/pocket-journal/issues"

# File extensions and formats
JOURNAL_FILE_EXTENSIONS = [".md", ".txt", ".journal"]
DEFAULT_FILE_EXTENSION = ".md"

# Application limits and defaults
MAX_RECENT_FILES = 10
MAX_JOURNAL_TITLE_LENGTH = 200
DEFAULT_FONT_SIZE = 11
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 72


def get_version_info() -> Dict[str, Any]:
    """Get complete version information as a dictionary."""
    return {
        "app_name": APP_NAME,
        "org_name": ORG_NAME,
        "version": VERSION,
        "build_date": BUILD_DATE,
        "channel": CHANNEL,
        "app_identifier": APP_IDENTIFIER,
        "is_dev": IS_DEV_CHANNEL,
        "is_beta": IS_BETA_CHANNEL,
        "is_release": IS_RELEASE_CHANNEL
    }


def get_version_string() -> str:
    """Get a formatted version string for display."""
    if IS_DEV_CHANNEL:
        return f"{VERSION}-dev ({BUILD_DATE})"
    elif IS_BETA_CHANNEL:
        return f"{VERSION}-beta"
    else:
        return VERSION


def get_app_title() -> str:
    """Get the application title for window titles."""
    if IS_DEV_CHANNEL:
        return f"{APP_NAME} v{VERSION} (Development)"
    elif IS_BETA_CHANNEL:
        return f"{APP_NAME} v{VERSION} (Beta)"
    else:
        return f"{APP_NAME} v{VERSION}"