"""
Basic tests for PocketJournal application.
"""

import pytest
from PySide6.QtWidgets import QApplication
from pocket_journal.main import PocketJournalMainWindow, PocketJournalApp


@pytest.fixture
def app(qtbot):
    """Create a QApplication instance for testing."""
    test_app = QApplication.instance()
    if test_app is None:
        test_app = QApplication([])
    return test_app


def test_main_window_creation(qtbot, app):
    """Test that the main window can be created successfully."""
    window = PocketJournalMainWindow()
    qtbot.addWidget(window)
    
    # Check that title contains the app name (it now includes version info)
    assert "PocketJournal" in window.windowTitle()
    assert window.minimumSize().width() == 600
    assert window.minimumSize().height() == 400


def test_app_creation():
    """Test that the PocketJournalApp can be created."""
    app = PocketJournalApp()
    assert app.app is None
    assert app.main_window is None


def test_window_has_central_widget(qtbot, app):
    """Test that the main window has a central widget."""
    window = PocketJournalMainWindow()
    qtbot.addWidget(window)
    
    central_widget = window.centralWidget()
    assert central_widget is not None