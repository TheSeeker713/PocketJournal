"""
Tests for Step 8 - Entry actions menu (⋯), export, delete, edit functionality.

Tests the complete entry actions system including:
- ⋯ menu for current entry: View in folder, Rename, Duplicate, Export, Delete
- Export destinations and formats (Markdown/TXT)
- Delete with undo toast for 10s
- Safe UX without data loss
- Open Data Folder command in Settings
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from PySide6.QtWidgets import QApplication, QTextEdit, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtGui import QAction

from src.pocket_journal.ui.entry_actions import (
    EntryActionsMenu, EntryActionsManager, UndoToastWidget, open_data_folder
)
from src.pocket_journal.data.entry_manager import Entry, EntryMetadata
from src.pocket_journal.ui.editor_panel_integrated import IntegratedEditorPanel
from src.pocket_journal.settings import set_setting, get_setting


class TestUndoToastWidget:
    """Test the undo toast widget."""
    
    def test_toast_initialization(self, app):
        """Test undo toast widget initialization."""
        message = "Entry deleted"
        toast = UndoToastWidget(message, timeout_ms=5000)
        
        assert toast.timeout_ms == 5000
        assert toast.message_label.text() == message
        assert toast.progress_bar.value() == 100
        assert toast.undo_button.text() == "UNDO"
    
    def test_toast_progress_updates(self, app, qtbot):
        """Test that progress bar updates correctly."""
        toast = UndoToastWidget("Test message", timeout_ms=1000)
        
        # Initial value should be 100
        assert toast.progress_bar.value() == 100
        
        # Wait a bit and check progress decreased
        qtbot.wait(200)
        assert toast.progress_bar.value() < 100
    
    def test_toast_timeout_signal(self, app, qtbot):
        """Test that timeout signal is emitted."""
        toast = UndoToastWidget("Test message", timeout_ms=100)
        
        with qtbot.waitSignal(toast.toast_expired, timeout=200):
            pass  # Wait for timeout signal
    
    def test_toast_undo_signal(self, app, qtbot):
        """Test that undo signal is emitted when button clicked."""
        toast = UndoToastWidget("Test message", timeout_ms=5000)
        
        with qtbot.waitSignal(toast.undo_requested):
            qtbot.mouseClick(toast.undo_button, Qt.MouseButton.LeftButton)


class TestEntryActionsMenu:
    """Test the entry actions menu."""
    
    @pytest.fixture
    def sample_entry(self):
        """Create a sample entry for testing."""
        metadata = EntryMetadata(
            id="test-entry-123",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            title="Test Entry Title",
            subtitle="Test subtitle",
            tags=["test", "sample"],
            word_count=50,
            path="/path/to/test-entry.md"
        )
        
        entry = Entry("This is test content for the entry.", metadata)
        return entry
    
    def test_menu_initialization(self, app, sample_entry):
        """Test entry actions menu initialization."""
        menu = EntryActionsMenu(sample_entry)
        
        assert menu.entry == sample_entry
        assert menu.entry_manager is not None
        
        # Check that menu has expected actions
        actions = menu.actions()
        action_texts = [action.text() for action in actions if not action.isSeparator()]
        
        expected_actions = [
            "📁 View in Folder",
            "✏️ Rename Entry", 
            "📄 Duplicate Entry",
            "🗑️ Delete Entry"
        ]
        
        for expected in expected_actions:
            assert any(expected in text for text in action_texts)
        
        # Check export submenu exists
        export_submenu = None
        for action in actions:
            if action.menu() and "Export" in action.text():
                export_submenu = action.menu()
                break
        
        assert export_submenu is not None
        export_actions = [action.text() for action in export_submenu.actions()]
        assert "Export as Markdown (.md)" in export_actions
        assert "Export as Text (.txt)" in export_actions
    
    def test_menu_signals_emitted(self, app, sample_entry, qtbot):
        """Test that menu actions emit correct signals."""
        menu = EntryActionsMenu(sample_entry)
        
        # Test view in folder signal
        with qtbot.waitSignal(menu.view_in_folder_requested):
            menu._on_view_in_folder()
        
        # Test rename signal
        with patch('PySide6.QtWidgets.QInputDialog.getText') as mock_input:
            mock_input.return_value = ("New Title", True)
            with qtbot.waitSignal(menu.rename_requested):
                menu._on_rename()
        
        # Test duplicate signal
        with qtbot.waitSignal(menu.duplicate_requested):
            menu._on_duplicate()
        
        # Test delete signal
        with patch('PySide6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = mock_question.return_value.Yes
            with qtbot.waitSignal(menu.delete_requested):
                menu._on_delete()
    
    def test_export_dialog_handling(self, app, sample_entry):
        """Test export dialog and file selection."""
        menu = EntryActionsMenu(sample_entry)
        
        with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("/path/to/export.md", "Markdown Files (*.md)")
            
            with patch.object(menu, 'export_requested') as mock_signal:
                menu._on_export("markdown")
                mock_signal.emit.assert_called_once()


class TestEntryActionsManager:
    """Test the entry actions manager."""
    
    @pytest.fixture
    def temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_entry_file(self, temp_directory):
        """Create a sample entry file for testing."""
        content = """---
id: test-entry-123
created_at: '2024-01-01T10:00:00+00:00'
updated_at: '2024-01-01T10:00:00+00:00'
title: Test Entry Title
subtitle: Test subtitle
tags:
- test
- sample
word_count: 10
path: ''
---

This is test content for the entry.
"""
        entry_file = temp_directory / "test-entry.md"
        entry_file.write_text(content, encoding='utf-8')
        return entry_file
    
    def test_manager_initialization(self, app):
        """Test entry actions manager initialization."""
        manager = EntryActionsManager()
        
        assert manager.entry_manager is not None
        assert manager.deleted_entries == {}
    
    def test_create_actions_menu(self, app):
        """Test creating an actions menu for an entry."""
        manager = EntryActionsManager()
        
        metadata = EntryMetadata(
            id="test-123",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            title="Test",
            subtitle="",
            tags=[],
            word_count=0,
            path="/test/path.md"
        )
        entry = Entry("Test content", metadata)
        
        menu = manager.create_actions_menu(entry)
        
        assert isinstance(menu, EntryActionsMenu)
        assert menu.entry == entry
    
    @patch('subprocess.run')
    @patch('pathlib.Path.resolve')
    def test_view_in_folder_windows(self, mock_resolve, mock_subprocess, app):
        """Test view in folder functionality on Windows."""
        manager = EntryActionsManager()
        mock_resolve.return_value = Path("C:/test/file.md")
        
        with patch('sys.platform', 'win32'):
            manager.view_in_folder("C:\\test\\file.md")
            mock_subprocess.assert_called_once_with(
                ["explorer", "/select,", "C:\\test\\file.md"], check=True
            )
    
    @patch('subprocess.run')
    @patch('pathlib.Path.resolve')
    def test_view_in_folder_macos(self, mock_resolve, mock_subprocess, app):
        """Test view in folder functionality on macOS."""
        manager = EntryActionsManager()
        mock_resolve.return_value = Path("/Users/test/file.md")
        
        with patch('sys.platform', 'darwin'):
            manager.view_in_folder("/Users/test/file.md")
            mock_subprocess.assert_called_once_with(
                ["open", "-R", "/Users/test/file.md"], check=True
            )
    
    @patch('subprocess.run')
    @patch('pathlib.Path.resolve')
    def test_view_in_folder_linux(self, mock_resolve, mock_subprocess, app):
        """Test view in folder functionality on Linux."""
        manager = EntryActionsManager()
        mock_resolve.return_value = Path("/home/test/file.md")
        
        with patch('sys.platform', 'linux'):
            manager.view_in_folder("/home/test/file.md")
            # Linux opens parent directory
            mock_subprocess.assert_called_once_with(
                ["xdg-open", "/home/test"], check=True
            )
    
    def test_rename_entry(self, app, temp_directory, sample_entry_file):
        """Test renaming an entry."""
        manager = EntryActionsManager()
        original_path = str(sample_entry_file)
        new_title = "Renamed Entry Title"
        
        with patch.object(manager, 'entry_renamed') as mock_signal:
            manager.rename_entry(original_path, new_title)
            mock_signal.emit.assert_called_once()
            
            # Check that file was renamed
            assert not sample_entry_file.exists()
            
            # Find the new file
            renamed_files = list(temp_directory.glob("*renamed*entry*title*.md"))
            assert len(renamed_files) == 1
            
            # Check content was updated
            new_content = renamed_files[0].read_text(encoding='utf-8')
            assert new_title in new_content
    
    def test_duplicate_entry(self, app, temp_directory, sample_entry_file):
        """Test duplicating an entry."""
        manager = EntryActionsManager()
        source_path = str(sample_entry_file)
        
        with patch.object(manager, 'entry_duplicated') as mock_signal:
            manager.duplicate_entry(source_path)
            mock_signal.emit.assert_called_once()
            
            # Check that original file still exists
            assert sample_entry_file.exists()
            
            # Check that duplicate was created
            md_files = list(temp_directory.glob("*.md"))
            assert len(md_files) == 2  # original + duplicate
            
            # Find the duplicate
            duplicate_files = [f for f in md_files if "copy" in f.name.lower()]
            assert len(duplicate_files) == 1
            
            # Check duplicate has modified title
            duplicate_content = duplicate_files[0].read_text(encoding='utf-8')
            assert "Copy" in duplicate_content
    
    def test_export_entry_markdown(self, app, temp_directory, sample_entry_file):
        """Test exporting entry as markdown."""
        manager = EntryActionsManager()
        source_path = str(sample_entry_file)
        destination = temp_directory / "exported.md"
        
        with patch.object(manager, 'entry_exported') as mock_signal:
            manager.export_entry(source_path, str(destination), "markdown")
            mock_signal.emit.assert_called_once()
            
            # Check export file was created
            assert destination.exists()
            
            # Check content includes front-matter
            export_content = destination.read_text(encoding='utf-8')
            assert export_content.startswith("---")
            assert "title: Test Entry Title" in export_content
    
    def test_export_entry_text(self, app, temp_directory, sample_entry_file):
        """Test exporting entry as plain text."""
        manager = EntryActionsManager()
        source_path = str(sample_entry_file)
        destination = temp_directory / "exported.txt"
        
        with patch.object(manager, 'entry_exported') as mock_signal:
            manager.export_entry(source_path, str(destination), "text")
            mock_signal.emit.assert_called_once()
            
            # Check export file was created
            assert destination.exists()
            
            # Check content excludes front-matter
            export_content = destination.read_text(encoding='utf-8')
            assert not export_content.startswith("---")
            assert "This is test content for the entry." in export_content
    
    def test_delete_entry_with_backup(self, app, temp_directory, sample_entry_file):
        """Test deleting an entry creates backup for undo."""
        manager = EntryActionsManager()
        file_path = str(sample_entry_file)
        original_content = sample_entry_file.read_text(encoding='utf-8')
        
        with patch.object(manager, 'entry_deleted') as mock_signal:
            with patch.object(manager, 'show_toast') as mock_toast:
                manager.delete_entry(file_path)
                
                mock_signal.emit.assert_called_once_with(file_path)
                mock_toast.emit.assert_called_once()
                
                # Check file was deleted
                assert not sample_entry_file.exists()
                
                # Check backup was created
                assert file_path in manager.deleted_entries
                backup = manager.deleted_entries[file_path]
                assert backup['content'] == original_content
                assert backup['path'] == file_path
    
    def test_restore_entry(self, app, temp_directory, sample_entry_file):
        """Test restoring a deleted entry."""
        manager = EntryActionsManager()
        file_path = str(sample_entry_file)
        
        # First delete the entry
        original_content = sample_entry_file.read_text(encoding='utf-8')
        manager.delete_entry(file_path)
        
        # Then restore it
        with patch.object(manager, 'entry_restored') as mock_signal:
            with patch.object(manager, 'hide_toast') as mock_hide:
                manager.restore_entry(file_path)
                
                mock_signal.emit.assert_called_once_with(file_path)
                mock_hide.emit.assert_called_once()
                
                # Check file was restored
                assert sample_entry_file.exists()
                restored_content = sample_entry_file.read_text(encoding='utf-8')
                assert restored_content == original_content
                
                # Check backup was cleaned up
                assert file_path not in manager.deleted_entries


class TestIntegratedEditorPanelEntryActions:
    """Test entry actions integration in the editor panel."""
    
    def test_entry_actions_manager_initialization(self, app):
        """Test that entry actions manager is initialized in editor panel."""
        with patch('src.pocket_journal.ui.editor_panel_integrated.AutosaveManager'):
            with patch('src.pocket_journal.ui.editor_panel_integrated.EntryLifecycleManager'):
                panel = IntegratedEditorPanel()
                
                assert panel.entry_actions_manager is not None
                assert isinstance(panel.entry_actions_manager, EntryActionsManager)
    
    def test_more_button_shows_menu_with_entry(self, app):
        """Test that more button shows actions menu when entry exists."""
        with patch('src.pocket_journal.ui.editor_panel_integrated.AutosaveManager'):
            with patch('src.pocket_journal.ui.editor_panel_integrated.EntryLifecycleManager'):
                panel = IntegratedEditorPanel()
                
                # Mock current entry
                mock_entry = Mock()
                mock_entry.metadata.path = "/test/path.md"
                panel.autosave_manager = Mock()
                panel.autosave_manager.current_entry = mock_entry
                
                # Mock menu creation and execution
                with patch.object(panel.entry_actions_manager, 'create_actions_menu') as mock_create:
                    mock_menu = Mock()
                    mock_create.return_value = mock_menu
                    
                    panel._on_more_clicked()
                    
                    mock_create.assert_called_once_with(mock_entry, panel)
                    mock_menu.exec.assert_called_once()
    
    def test_more_button_no_entry_warning(self, app):
        """Test that more button shows warning when no entry exists."""
        with patch('src.pocket_journal.ui.editor_panel_integrated.AutosaveManager'):
            with patch('src.pocket_journal.ui.editor_panel_integrated.EntryLifecycleManager'):
                panel = IntegratedEditorPanel()
                
                # No current entry
                panel.autosave_manager = Mock()
                panel.autosave_manager.current_entry = None
                
                with patch('PySide6.QtWidgets.QMessageBox.information') as mock_message:
                    panel._on_more_clicked()
                    mock_message.assert_called_once()
    
    def test_toast_display_integration(self, app):
        """Test that undo toasts are displayed correctly in panel."""
        with patch('src.pocket_journal.ui.editor_panel_integrated.AutosaveManager'):
            with patch('src.pocket_journal.ui.editor_panel_integrated.EntryLifecycleManager'):
                panel = IntegratedEditorPanel()
                
                # Create mock toast
                mock_toast = Mock()
                
                # Test showing toast
                panel._show_toast(mock_toast)
                assert panel.current_toast == mock_toast
                mock_toast.setParent.assert_called_with(panel)
                mock_toast.show.assert_called_once()
                
                # Test hiding toast
                panel._hide_toast()
                assert panel.current_toast is None
                mock_toast.hide.assert_called_once()


class TestOpenDataFolder:
    """Test the open data folder functionality."""
    
    @patch('subprocess.run')
    def test_open_data_folder_windows(self, mock_subprocess):
        """Test opening data folder on Windows."""
        with patch('sys.platform', 'win32'):
            with patch('src.pocket_journal.ui.entry_actions.get_setting') as mock_setting:
                mock_setting.return_value = "/test/data"
                
                open_data_folder()
                mock_subprocess.assert_called_once_with(
                    ["explorer", str(Path("/test/data"))], check=True
                )
    
    @patch('subprocess.run')
    def test_open_data_folder_macos(self, mock_subprocess):
        """Test opening data folder on macOS."""
        with patch('sys.platform', 'darwin'):
            with patch('src.pocket_journal.ui.entry_actions.get_setting') as mock_setting:
                mock_setting.return_value = "/test/data"
                
                open_data_folder()
                mock_subprocess.assert_called_once_with(
                    ["open", str(Path("/test/data"))], check=True
                )
    
    @patch('subprocess.run')
    def test_open_data_folder_linux(self, mock_subprocess):
        """Test opening data folder on Linux."""
        with patch('sys.platform', 'linux'):
            with patch('src.pocket_journal.ui.entry_actions.get_setting') as mock_setting:
                mock_setting.return_value = "/test/data"
                
                open_data_folder()
                mock_subprocess.assert_called_once_with(
                    ["xdg-open", str(Path("/test/data"))], check=True
                )
    
    def test_open_data_folder_error_handling(self):
        """Test error handling when opening data folder fails."""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
                open_data_folder()
                mock_warning.assert_called_once()


class TestStep8AcceptanceCriteria:
    """Test Step 8 acceptance criteria specifically."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_all_actions_work_without_data_loss(self, app, temp_workspace):
        """Test: All actions work without data loss."""
        # Create sample entry
        entry_file = temp_workspace / "test-entry.md"
        content = """---
id: test-123
created_at: '2024-01-01T10:00:00+00:00'
updated_at: '2024-01-01T10:00:00+00:00'
title: Original Title
subtitle: Original subtitle
tags: []
word_count: 5
path: ''
---

Original content here.
"""
        entry_file.write_text(content, encoding='utf-8')
        
        manager = EntryActionsManager()
        
        # Test rename preserves data
        manager.rename_entry(str(entry_file), "New Title")
        renamed_files = list(temp_workspace.glob("*new*title*.md"))
        assert len(renamed_files) == 1
        new_content = renamed_files[0].read_text(encoding='utf-8')
        assert "Original content here." in new_content
        assert "New Title" in new_content
        
        # Test duplicate preserves data
        manager.duplicate_entry(str(renamed_files[0]))
        all_files = list(temp_workspace.glob("*.md"))
        assert len(all_files) == 2
        
        # Test export preserves data
        export_path = temp_workspace / "export.md"
        manager.export_entry(str(renamed_files[0]), str(export_path), "markdown")
        assert export_path.exists()
        export_content = export_path.read_text(encoding='utf-8')
        assert "Original content here." in export_content
    
    def test_delete_shows_reversible_snackbar(self, app, temp_workspace):
        """Test: Delete shows a reversible snackbar/toast."""
        entry_file = temp_workspace / "test-entry.md"
        entry_file.write_text("Test content", encoding='utf-8')
        
        manager = EntryActionsManager()
        
        toast_shown = False
        def mock_show_toast(toast_widget):
            nonlocal toast_shown
            toast_shown = True
            assert isinstance(toast_widget, UndoToastWidget)
            assert "deleted" in toast_widget.message_label.text().lower()
        
        manager.show_toast.connect(mock_show_toast)
        
        # Delete entry
        manager.delete_entry(str(entry_file))
        
        assert toast_shown
        assert not entry_file.exists()
        assert str(entry_file) in manager.deleted_entries
    
    def test_export_files_are_correct(self, app, temp_workspace):
        """Test: Export files are correct."""
        # Create sample entry
        entry_file = temp_workspace / "source-entry.md"
        content = """---
id: test-123
created_at: '2024-01-01T10:00:00+00:00'
updated_at: '2024-01-01T10:00:00+00:00'
title: Export Test
subtitle: Testing export
tags:
- export
- test
word_count: 8
path: ''
---

This is the main content.
With multiple lines.
"""
        entry_file.write_text(content, encoding='utf-8')
        
        manager = EntryActionsManager()
        
        # Test markdown export
        md_export = temp_workspace / "export.md"
        manager.export_entry(str(entry_file), str(md_export), "markdown")
        
        assert md_export.exists()
        md_content = md_export.read_text(encoding='utf-8')
        assert md_content.startswith("---")
        assert "title: Export Test" in md_content
        assert "This is the main content." in md_content
        
        # Test text export
        txt_export = temp_workspace / "export.txt"
        manager.export_entry(str(entry_file), str(txt_export), "text")
        
        assert txt_export.exists()
        txt_content = txt_export.read_text(encoding='utf-8')
        assert not txt_content.startswith("---")
        assert "title: Export Test" not in txt_content
        assert "This is the main content." in txt_content
    
    def test_menu_actions_complete_set(self, app):
        """Test: ⋯ menu has complete set of actions."""
        metadata = EntryMetadata(
            id="test-123",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            title="Test Entry",
            subtitle="Test subtitle",
            tags=["test"],
            word_count=10,
            path="/test/entry.md"
        )
        entry = Entry("Test content", metadata)
        
        menu = EntryActionsMenu(entry)
        actions = menu.actions()
        action_texts = [action.text() for action in actions if not action.isSeparator()]
        
        # Required actions from Step 8
        required_actions = [
            "View in Folder",      # View in folder
            "Rename Entry",        # Rename (update filename + front-matter title safely)  
            "Duplicate Entry",     # Duplicate
            "Export",              # Export (Markdown/TXT)
            "Delete Entry"         # Delete (with undo toast for 10s)
        ]
        
        for required in required_actions:
            assert any(required in text for text in action_texts), f"Missing action: {required}"
    
    def test_open_data_folder_command_available(self, app):
        """Test: "Open Data Folder" command is available under Files in Settings."""
        # This is tested by verifying the open_data_folder function exists and works
        # The UI integration is tested in the settings dialog tests
        
        with patch('subprocess.run') as mock_subprocess:
            with patch('sys.platform', 'win32'):
                with patch('src.pocket_journal.ui.entry_actions.get_setting') as mock_setting:
                    mock_setting.return_value = "/test/data"
                    
                    # Function should be callable and work
                    open_data_folder()
                    mock_subprocess.assert_called_once()
    
    def test_export_destinations_configurable(self, app, temp_workspace):
        """Test: Export destinations are pickable; default to /Exports subfolder."""
        set_setting("data_directory", str(temp_workspace))
        
        metadata = EntryMetadata(
            id="test-123",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            title="Export Test",
            subtitle="",
            tags=[],
            word_count=5,
            path=str(temp_workspace / "entry.md")
        )
        entry = Entry("Test content", metadata)
        
        menu = EntryActionsMenu(entry)
        
        # Mock the file dialog to verify default directory
        with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = (str(temp_workspace / "Exports" / "export.md"), "")
            
            menu._on_export("markdown")
            
            # Check that dialog was called with Exports subdirectory as default
            call_args = mock_dialog.call_args[0]
            default_path = call_args[2]  # Third argument is default path
            assert "Exports" in default_path
    
    def test_undo_functionality_within_timeout(self, app, temp_workspace):
        """Test: Delete undo functionality works within 10-second timeout."""
        entry_file = temp_workspace / "test-entry.md"
        original_content = "Original content for undo test"
        entry_file.write_text(original_content, encoding='utf-8')
        
        manager = EntryActionsManager()
        
        # Delete the entry
        manager.delete_entry(str(entry_file))
        assert not entry_file.exists()
        
        # Restore within timeout
        manager.restore_entry(str(entry_file))
        
        # Check file was restored
        assert entry_file.exists()
        restored_content = entry_file.read_text(encoding='utf-8')
        assert restored_content == original_content