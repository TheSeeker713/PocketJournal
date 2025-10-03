"""User interface components for PocketJournal."""

from .micro_launcher import CircularLauncher
from .editor_panel import QuickEditorPanel
from .editor_panel_integrated import IntegratedEditorPanel
from .launcher_manager import LauncherManager
from .system_tray import SystemTrayManager, DockModeManager, StartupManager
from .settings_dialog import SettingsDialog, show_settings_dialog
from .entry_actions import EntryActionsManager, EntryActionsMenu, open_data_folder
from .recent_and_search import RecentEntriesPopover, SearchDialog, FastSearchEngine

__all__ = [
    'CircularLauncher',
    'QuickEditorPanel',
    'IntegratedEditorPanel',
    'LauncherManager',
    'SystemTrayManager',
    'DockModeManager',
    'StartupManager',
    'SettingsDialog',
    'show_settings_dialog',
    'EntryActionsManager',
    'EntryActionsMenu',
    'open_data_folder',
    'RecentEntriesPopover',
    'SearchDialog',
    'FastSearchEngine'
]