"""
Tests for the micro-launcher functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtGui import QMouseEvent

from pocket_journal.ui.micro_launcher import CircularLauncher
from pocket_journal.ui.editor_panel import QuickEditorPanel
from pocket_journal.ui.launcher_manager import LauncherManager


@pytest.fixture
def app(qtbot):
    """Create a QApplication instance for testing."""
    test_app = QApplication.instance()
    if test_app is None:
        test_app = QApplication([])
    return test_app


class TestCircularLauncher:
    """Test the circular launcher component."""
    
    def test_launcher_creation(self, qtbot, app):
        """Test that the circular launcher can be created."""
        launcher = CircularLauncher()
        qtbot.addWidget(launcher)
        
        assert launcher.circle_size >= 32
        assert launcher.circle_size <= 64
        assert launcher.last_corner in ["top-left", "top-right", "bottom-left", "bottom-right"]
    
    def test_launcher_window_properties(self, qtbot, app):
        """Test that the launcher has correct window properties."""
        launcher = CircularLauncher()
        qtbot.addWidget(launcher)
        
        # Should be frameless and always on top
        flags = launcher.windowFlags()
        assert Qt.WindowType.FramelessWindowHint in flags
        assert Qt.WindowType.WindowStaysOnTopHint in flags
        
        # Should have fixed size
        assert launcher.size().width() == launcher.circle_size
        assert launcher.size().height() == launcher.circle_size
    
    def test_corner_detection(self, qtbot, app):
        """Test corner detection logic."""
        launcher = CircularLauncher()
        qtbot.addWidget(launcher)
        
        # Test corner detection with mock screen geometry
        with patch('PySide6.QtWidgets.QApplication.primaryScreen') as mock_screen:
            mock_geometry = MagicMock()
            mock_geometry.width.return_value = 1920
            mock_geometry.height.return_value = 1080
            mock_screen.return_value.availableGeometry.return_value = mock_geometry
            
            # Test top-left
            corner = launcher.get_nearest_corner(QPoint(10, 10))
            assert corner == "top-left"
            
            # Test top-right
            corner = launcher.get_nearest_corner(QPoint(1900, 10))
            assert corner == "top-right"
            
            # Test bottom-left
            corner = launcher.get_nearest_corner(QPoint(10, 1060))
            assert corner == "bottom-left"
            
            # Test bottom-right
            corner = launcher.get_nearest_corner(QPoint(1900, 1060))
            assert corner == "bottom-right"
    
    def test_mouse_events(self, qtbot, app):
        """Test mouse event handling."""
        launcher = CircularLauncher()
        qtbot.addWidget(launcher)
        
        # Test mouse press starts dragging
        press_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(24, 24),  # Center of 48px circle
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        launcher.mousePressEvent(press_event)
        assert launcher.is_dragging
    
    def test_expand_signal(self, qtbot, app):
        """Test that expand signal is emitted on click."""
        launcher = CircularLauncher()
        qtbot.addWidget(launcher)
        
        # Connect signal to test
        expand_called = False
        def on_expand():
            nonlocal expand_called
            expand_called = True
        
        launcher.expand_requested.connect(on_expand)
        
        # Simulate click (press and release without dragging)
        launcher.is_dragging = False
        release_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPoint(24, 24),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        launcher.mouseReleaseEvent(release_event)
        assert expand_called


class TestQuickEditorPanel:
    """Test the quick editor panel component."""
    
    def test_panel_creation(self, qtbot, app):
        """Test that the editor panel can be created."""
        panel = QuickEditorPanel()
        qtbot.addWidget(panel)
        
        assert panel.expanded_size.width() > 0
        assert panel.expanded_size.height() > 0
        assert not panel.is_expanded
    
    def test_panel_window_properties(self, qtbot, app):
        """Test that the panel has correct window properties."""
        panel = QuickEditorPanel()
        qtbot.addWidget(panel)
        
        # Should be frameless and always on top
        flags = panel.windowFlags()
        assert Qt.WindowType.FramelessWindowHint in flags
        assert Qt.WindowType.WindowStaysOnTopHint in flags
    
    def test_content_handling(self, qtbot, app):
        """Test content loading and saving."""
        panel = QuickEditorPanel()
        qtbot.addWidget(panel)
        
        # Test setting content
        test_content = "This is a test note."
        panel.text_editor.setPlainText(test_content)
        
        # Check that word count updates (count should be 5: "This", "is", "a", "test", "note.")
        assert "5 words" in panel.word_count_label.text()
        
        # Test content saving (would need to mock settings)
        panel.save_content()
    
    def test_expand_animation_setup(self, qtbot, app):
        """Test that expand animation can be set up."""
        panel = QuickEditorPanel()
        qtbot.addWidget(panel)
        
        # Test expand from position
        source_pos = QPoint(100, 100)
        source_size = QSize(48, 48)
        
        # This should set up animations (though we won't run them in test)
        panel.expand_from_position(source_pos, source_size)
        assert panel.is_expanded
    
    def test_collapse_signal(self, qtbot, app):
        """Test that collapse signal is emitted correctly."""
        panel = QuickEditorPanel()
        qtbot.addWidget(panel)
        
        collapse_called = False
        def on_collapse():
            nonlocal collapse_called
            collapse_called = True
        
        panel.collapse_requested.connect(on_collapse)
        
        # Test ESC key
        from PySide6.QtGui import QKeyEvent
        esc_event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier
        )
        
        panel.keyPressEvent(esc_event)
        assert collapse_called


class TestLauncherManager:
    """Test the launcher manager coordination."""
    
    def test_manager_creation(self, qtbot, app):
        """Test that the launcher manager can be created."""
        manager = LauncherManager()
        
        assert manager.circular_launcher is not None
        assert manager.editor_panel is not None
        assert not manager.is_panel_expanded
        assert manager.launcher_visible
    
    def test_expand_collapse_coordination(self, qtbot, app):
        """Test expand and collapse coordination."""
        manager = LauncherManager()
        
        # Test expand
        manager.expand_panel()
        assert manager.is_panel_expanded
        
        # Test collapse
        manager.collapse_panel()
        assert not manager.is_panel_expanded
    
    def test_toggle_functionality(self, qtbot, app):
        """Test toggle between expanded and collapsed states."""
        manager = LauncherManager()
        
        initial_state = manager.is_panel_expanded
        manager.toggle_panel()
        assert manager.is_panel_expanded != initial_state
        
        manager.toggle_panel()
        assert manager.is_panel_expanded == initial_state
    
    def test_launcher_visibility(self, qtbot, app):
        """Test launcher visibility management."""
        manager = LauncherManager()
        
        # Test hiding launcher
        manager.set_launcher_visible(False)
        assert not manager.launcher_visible
        
        # Test showing launcher
        manager.set_launcher_visible(True)
        assert manager.launcher_visible
    
    def test_corner_management(self, qtbot, app):
        """Test corner position management."""
        manager = LauncherManager()
        
        # Test setting corner
        test_corner = "bottom-left"
        manager.set_launcher_corner(test_corner)
        assert manager.get_launcher_corner() == test_corner
    
    def test_shutdown_cleanup(self, qtbot, app):
        """Test proper cleanup on shutdown."""
        manager = LauncherManager()
        
        # Should not raise any exceptions
        manager.shutdown()