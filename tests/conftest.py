"""
Shared test fixtures for PocketJournal tests.
"""

import pytest
import sys
import tempfile
from pathlib import Path

from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def app():
    """Create a QApplication instance for testing."""
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app
    # Cleanup happens automatically when tests finish


@pytest.fixture
def qtbot():
    """Provide a qtbot for Qt widget testing."""
    try:
        from pytestqt.qtbot import QtBot
        return QtBot()
    except ImportError:
        # If pytest-qt is not available, create a minimal mock
        class MockQtBot:
            def wait(self, ms):
                pass
            
            def waitSignal(self, signal, timeout=1000):
                class SignalWaiter:
                    def __enter__(self):
                        return self
                    def __exit__(self, *args):
                        pass
                return SignalWaiter()
            
            def mouseClick(self, widget, button):
                pass
        
        return MockQtBot()


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    import shutil
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    import shutil
    shutil.rmtree(temp_dir)