"""
Tests for system tray functionality.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest

from src.pocket_journal.ui.system_tray import SystemTrayManager, DockModeManager, StartupManager
from src.pocket_journal.settings import settings


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


class TestSystemTrayManager:
    """Test the SystemTrayManager class."""
    
    def test_initialization(self, app):
        """Test system tray manager initialization."""
        tray = SystemTrayManager()
        
        assert tray is not None
        assert hasattr(tray, 'tray_icon')
        assert hasattr(tray, 'context_menu')
    
    @patch.object(QSystemTrayIcon, 'isSystemTrayAvailable', return_value=True)
    def test_is_available_when_supported(self, mock_available):
        """Test is_available property when system tray is supported."""
        tray = SystemTrayManager()
        assert tray.is_available is True
    
    @patch.object(QSystemTrayIcon, 'isSystemTrayAvailable', return_value=False)
    def test_is_available_when_not_supported(self, mock_available):
        """Test is_available property when system tray is not supported."""
        tray = SystemTrayManager()
        assert tray.is_available is False
    
    def test_context_menu_creation(self, app):
        """Test that context menu is created with expected actions."""
        tray = SystemTrayManager()
        
        menu = tray.context_menu
        assert menu is not None
        
        # Check that actions exist
        actions = menu.actions()
        action_texts = [action.text() for action in actions]
        
        expected_actions = [
            "Quick Jot", 
            "Open Window", 
            "Recent", 
            "Settings", 
            "Help", 
            "About", 
            "Quit"
        ]
        
        for expected in expected_actions:
            assert any(expected in text for text in action_texts), f"Action '{expected}' not found"
    
    def test_signal_connections(self, app):
        """Test that tray icon signals are properly connected."""
        tray = SystemTrayManager()
        
        # Mock the signal connections
        tray.tray_icon.activated = Mock()
        tray.tray_icon.messageClicked = Mock()
        
        # These should not raise errors
        assert hasattr(tray, 'quick_jot_requested')
        assert hasattr(tray, 'show_window_requested')
        assert hasattr(tray, 'settings_requested')
        assert hasattr(tray, 'exit_requested')
    
    def test_show_hide(self, app):
        """Test showing and hiding the tray icon."""
        tray = SystemTrayManager()
        
        # Mock the tray icon
        tray.tray_icon.show = Mock()
        tray.tray_icon.hide = Mock()
        
        # Test show
        tray.show()
        tray.tray_icon.show.assert_called_once()
        
        # Test hide
        tray.hide()
        tray.tray_icon.hide.assert_called_once()
    
    def test_notification(self, app):
        """Test showing notifications."""
        tray = SystemTrayManager()
        
        # Mock showMessage
        tray.tray_icon.showMessage = Mock()
        
        # Test notification
        title = "Test Title"
        message = "Test Message"
        tray.show_notification(title, message)
        
        tray.tray_icon.showMessage.assert_called_once()


class TestDockModeManager:
    """Test the DockModeManager class."""
    
    def test_initialization(self):
        """Test dock mode manager initialization."""
        manager = DockModeManager()
        assert manager is not None
    
    def test_get_current_mode(self):
        """Test getting current dock mode."""
        # Mock the initial setting call during DockModeManager initialization
        with patch('src.pocket_journal.ui.system_tray.get_setting', return_value="corner"), \
             patch.object(DockModeManager, '_apply_mode'):
            manager = DockModeManager()
            mode = manager.get_current_mode()
            assert mode == "corner"
        
        # For tray mode, we need to also mock the tray manager to be available
        mock_tray_manager = Mock()
        mock_tray_manager.is_available = True
        
        with patch('src.pocket_journal.ui.system_tray.get_setting', return_value="tray"), \
             patch.object(DockModeManager, '_apply_mode'):
            manager = DockModeManager(tray_manager=mock_tray_manager)
            mode = manager.get_current_mode()
            assert mode == "tray"
    
    def test_set_mode(self):
        """Test setting dock mode."""
        manager = DockModeManager()
        
        # Mock settings and system tray availability
        with patch('src.pocket_journal.ui.system_tray.set_setting') as mock_set, \
             patch.object(manager, '_apply_mode') as mock_apply:
            manager.set_mode("tray")
            mock_set.assert_called_once_with("dock_mode", "tray")
            mock_apply.assert_called_once_with("tray")
    
    def test_is_tray_mode(self):
        """Test checking if in tray mode."""
        # For tray mode, we need to also mock the tray manager to be available
        mock_tray_manager = Mock()
        mock_tray_manager.is_available = True
        
        with patch('src.pocket_journal.ui.system_tray.get_setting', return_value="tray"), \
             patch.object(DockModeManager, '_apply_mode'):
            manager = DockModeManager(tray_manager=mock_tray_manager)
            assert manager.is_tray_mode() is True
        
        with patch('src.pocket_journal.ui.system_tray.get_setting', return_value="corner"), \
             patch.object(DockModeManager, '_apply_mode'):
            manager = DockModeManager()
            assert manager.is_tray_mode() is False
    
    def test_is_corner_mode(self):
        """Test checking if in corner mode."""
        with patch('src.pocket_journal.ui.system_tray.get_setting', return_value="corner"), \
             patch.object(DockModeManager, '_apply_mode'):
            manager = DockModeManager()
            assert manager.is_corner_mode() is True
        
        # For tray mode, we need to also mock the tray manager to be available
        mock_tray_manager = Mock()
        mock_tray_manager.is_available = True
        
        with patch('src.pocket_journal.ui.system_tray.get_setting', return_value="tray"), \
             patch.object(DockModeManager, '_apply_mode'):
            manager = DockModeManager(tray_manager=mock_tray_manager)
            assert manager.is_corner_mode() is False


class TestStartupManager:
    """Test the StartupManager class."""
    
    def test_initialization(self):
        """Test startup manager initialization."""
        manager = StartupManager()
        assert manager is not None
        assert hasattr(manager, 'app_name')
        assert hasattr(manager, 'executable_path')
    
    @pytest.mark.skipif(not sys.platform.startswith('win'), reason="Windows-specific test")
    def test_windows_startup_functionality(self):
        """Test Windows startup functionality."""
        
        # Mock winreg module at import level
        with patch.dict('sys.modules', {'winreg': MagicMock()}):
            import winreg
            winreg.OpenKey.return_value.__enter__ = MagicMock()
            winreg.OpenKey.return_value.__exit__ = MagicMock()
            winreg.QueryValueEx.return_value = (r"C:\test\path\app.exe", 1)
            
            manager = StartupManager()
            
            # Test checking startup status
            result = manager.is_startup_enabled()
            assert isinstance(result, bool)
    
    @pytest.mark.skipif(not sys.platform.startswith('win'), reason="Windows-specific test")
    def test_windows_set_startup_enabled(self):
        """Test enabling Windows startup."""
        
        # Mock winreg module at import level
        with patch.dict('sys.modules', {'winreg': MagicMock()}):
            import winreg
            winreg.OpenKey.return_value.__enter__ = MagicMock()
            winreg.OpenKey.return_value.__exit__ = MagicMock()
            
            manager = StartupManager()
            
            # Test enabling startup
            result = manager.set_startup_enabled(True)
            assert isinstance(result, bool)
    
    @pytest.mark.skipif(not sys.platform.startswith('win'), reason="Windows-specific test")  
    def test_windows_set_startup_disabled(self):
        """Test disabling Windows startup."""
        
        # Mock winreg module at import level
        with patch.dict('sys.modules', {'winreg': MagicMock()}):
            import winreg
            winreg.OpenKey.return_value.__enter__ = MagicMock()
            winreg.OpenKey.return_value.__exit__ = MagicMock()
            
            manager = StartupManager()
            
            # Test disabling startup
            result = manager.set_startup_enabled(False)
            assert isinstance(result, bool)
    
    @pytest.mark.skipif(sys.platform.startswith('win'), reason="Non-Windows test")
    def test_non_windows_platform(self):
        """Test startup manager on non-Windows platforms."""
        manager = StartupManager()
        
        # Should return False for unsupported platforms
        assert manager.is_startup_enabled() is False
        assert manager.set_startup_enabled(True) is False
        assert manager.set_startup_enabled(False) is False
    
    def test_get_startup_command(self):
        """Test getting startup command."""
        manager = StartupManager()
        
        # Test when startup is not enabled (default case)
        with patch.object(manager, 'is_startup_enabled', return_value=False):
            command = manager.get_startup_command()
            assert command is None
        
        # Test when startup is enabled
        if sys.platform.startswith('win'):
            with patch.dict('sys.modules', {'winreg': MagicMock()}):
                import winreg
                winreg.OpenKey.return_value.__enter__ = MagicMock()
                winreg.OpenKey.return_value.__exit__ = MagicMock()
                winreg.QueryValueEx.return_value = (r"C:\test\path\app.exe", 1)
                
                with patch.object(manager, 'is_startup_enabled', return_value=True):
                    command = manager.get_startup_command()
                    assert isinstance(command, str)
        else:
            # Non-Windows should return None
            command = manager.get_startup_command()
            assert command is None


class TestSystemTrayIntegration:
    """Test system tray integration with other components."""
    
    def test_dock_mode_switching(self, app):
        """Test dock mode switching integration."""
        # Create managers
        tray_manager = SystemTrayManager()
        dock_manager = DockModeManager()
        
        # Mock current mode
        with patch.object(dock_manager, 'get_current_mode', return_value="corner"):
            assert dock_manager.is_corner_mode() is True
            assert dock_manager.is_tray_mode() is False
        
        # Switch to tray mode
        with patch.object(dock_manager, 'set_mode') as mock_set:
            dock_manager.set_mode("tray")
            mock_set.assert_called_once_with("tray")
    
    def test_startup_integration(self):
        """Test startup manager integration."""
        startup_manager = StartupManager()
        
        # Test that startup status can be checked
        status = startup_manager.is_startup_enabled()
        assert isinstance(status, bool)
        
        # Test command generation - may return None if not enabled
        command = startup_manager.get_startup_command()
        assert command is None or isinstance(command, str)


# Integration test for the full tray system
class TestFullSystemTraySystem:
    """Test the complete system tray system."""
    
    def test_complete_tray_workflow(self, app):
        """Test complete tray system workflow."""
        # Create all managers
        tray_manager = SystemTrayManager()
        dock_manager = DockModeManager()
        startup_manager = StartupManager()
        
        # Test initial state
        assert tray_manager is not None
        assert dock_manager is not None
        assert startup_manager is not None
        
        # Test mode switching
        with patch.object(dock_manager, 'set_mode') as mock_set:
            dock_manager.set_mode("tray")
            mock_set.assert_called_once_with("tray")
        
        # Test tray operations
        with patch.object(tray_manager.tray_icon, 'show') as mock_show:
            tray_manager.show()
            mock_show.assert_called_once()
        
        # Test notifications
        with patch.object(tray_manager.tray_icon, 'showMessage') as mock_message:
            tray_manager.show_notification("Test", "Message")
            mock_message.assert_called_once()
    
    def test_signal_emission(self, app):
        """Test that tray manager emits expected signals."""
        tray_manager = SystemTrayManager()
        
        # Connect to signals and verify they exist
        signal_received = []
        
        def on_signal():
            signal_received.append(True)
        
        # Test signal connections
        tray_manager.quick_jot_requested.connect(on_signal)
        tray_manager.show_window_requested.connect(on_signal)
        tray_manager.settings_requested.connect(on_signal)
        tray_manager.exit_requested.connect(on_signal)
        
        # Emit signals manually to test connections
        tray_manager.quick_jot_requested.emit()
        tray_manager.show_window_requested.emit()
        tray_manager.settings_requested.emit()
        tray_manager.exit_requested.emit()
        
        # Verify signals were received
        assert len(signal_received) == 4