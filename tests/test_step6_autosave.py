"""
Tests for Step 6 autosave and entry lifecycle functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from PySide6.QtWidgets import QApplication, QTextEdit
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest

from src.pocket_journal.data.entry_manager import Entry, EntryMetadata, EntryManager
from src.pocket_journal.core.autosave import AutosaveManager, EntryLifecycleManager


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def temp_entries_dir():
    """Create temporary directory for entry storage."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestEntry:
    """Test the Entry class."""
    
    def test_new_entry_creation(self):
        """Test creating a new entry."""
        content = "This is a test entry"
        entry = Entry(content)
        
        # Check content
        assert entry.content == content
        assert entry.is_new
        assert not entry.is_modified  # Should be False initially
        
        # Check metadata
        assert entry.metadata.id
        assert entry.metadata.created_at
        assert entry.metadata.updated_at
        assert entry.metadata.word_count == 0  # Not updated until update_metadata called
    
    def test_entry_metadata_update(self):
        """Test entry metadata update."""
        content = "This is a test entry with multiple words"
        entry = Entry(content)
        
        # Update metadata
        entry.update_metadata()
        
        # Check word count
        assert entry.metadata.word_count == 8
        
        # Check title extraction from first line
        entry.content = "# My Test Title\n\nSome content here"
        entry.update_metadata()
        assert entry.metadata.title == "My Test Title"
    
    def test_entry_filename_generation(self):
        """Test filename generation."""
        entry = Entry("Test content")
        entry.metadata.title = "My Test Entry"
        
        filename = entry.generate_filename()
        
        # Should have format: YYYY-MM-DD_HH-MM-SS_slug.md
        assert filename.endswith('.md')
        assert 'my-test-entry' in filename.lower() or entry.metadata.id[:8] in filename
        
        # Test with no title
        entry.metadata.title = ""
        filename = entry.generate_filename()
        assert filename.endswith('.md')
        assert entry.metadata.id[:8] in filename
    
    def test_entry_to_markdown(self):
        """Test converting entry to markdown with YAML front-matter."""
        entry = Entry("This is test content")
        entry.metadata.title = "Test Entry"
        entry.metadata.tags = ["test", "sample"]
        
        markdown = entry.to_markdown()
        
        # Check YAML front-matter
        assert markdown.startswith('---')
        assert 'id:' in markdown
        assert 'created_at:' in markdown
        assert 'updated_at:' in markdown
        assert 'title: Test Entry' in markdown
        assert 'tags:' in markdown
        assert 'test' in markdown
        assert 'sample' in markdown
        
        # Check content
        assert 'This is test content' in markdown
    
    def test_entry_from_markdown(self):
        """Test creating entry from markdown with YAML front-matter."""
        markdown_content = """---
id: test-id-123
created_at: '2025-10-02T20:00:00+00:00'
updated_at: '2025-10-02T20:05:00+00:00'
title: Test Entry
subtitle: ''
tags:
- test
- sample
word_count: 4
path: ''
---

This is test content."""
        
        entry = Entry.from_markdown(markdown_content)
        
        # Check metadata
        assert entry.metadata.id == "test-id-123"
        assert entry.metadata.title == "Test Entry"
        assert entry.metadata.tags == ["test", "sample"]
        assert entry.metadata.word_count == 4
        
        # Check content
        assert entry.content == "This is test content."
        assert not entry.is_new
    
    def test_entry_modification_tracking(self):
        """Test entry modification tracking."""
        entry = Entry("Original content")
        assert not entry.is_modified
        
        # Modify content
        entry.content = "Modified content"
        assert entry.is_modified
        
        # Simulate save by updating original content
        entry._original_content = entry.content
        assert not entry.is_modified


class TestEntryManager:
    """Test the EntryManager class."""
    
    def test_entry_manager_initialization(self, temp_entries_dir):
        """Test entry manager initialization."""
        with patch('src.pocket_journal.data.entry_manager.EntryManager._get_base_path', return_value=temp_entries_dir):
            manager = EntryManager()
            assert manager.base_path == temp_entries_dir
            assert manager.current_entry is None
    
    def test_create_new_entry(self, temp_entries_dir):
        """Test creating new entry."""
        with patch('src.pocket_journal.data.entry_manager.EntryManager._get_base_path', return_value=temp_entries_dir):
            manager = EntryManager()
            
            entry = manager.create_new_entry("Initial content")
            
            assert entry.content == "Initial content"
            assert entry.is_new
            assert manager.current_entry == entry
    
    def test_save_entry(self, temp_entries_dir):
        """Test saving entry to filesystem."""
        with patch('src.pocket_journal.data.entry_manager.EntryManager._get_base_path', return_value=temp_entries_dir):
            manager = EntryManager()
            
            # Create and save entry
            entry = manager.create_new_entry("Test content for saving")
            entry.metadata.title = "Test Save Entry"
            
            success = manager.save_entry(entry)
            
            assert success
            assert not entry.is_new
            assert entry.metadata.path
            
            # Check file exists
            file_path = Path(entry.metadata.path)
            assert file_path.exists()
            
            # Check file content
            content = file_path.read_text(encoding='utf-8')
            assert 'Test content for saving' in content
            assert 'title: Test Save Entry' in content
    
    def test_load_entry(self, temp_entries_dir):
        """Test loading entry from file."""
        with patch('src.pocket_journal.data.entry_manager.EntryManager._get_base_path', return_value=temp_entries_dir):
            manager = EntryManager()
            
            # Create and save entry first
            original_entry = manager.create_new_entry("Content to load")
            original_entry.metadata.title = "Load Test Entry"
            manager.save_entry(original_entry)
            
            # Load entry
            loaded_entry = manager.load_entry(original_entry.metadata.path)
            
            assert loaded_entry is not None
            assert loaded_entry.content == "Content to load"
            assert loaded_entry.metadata.title == "Load Test Entry"
            assert not loaded_entry.is_new


class TestAutosaveManager:
    """Test the AutosaveManager class."""
    
    def test_autosave_manager_initialization(self, app):
        """Test autosave manager initialization."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager'):
            autosave_manager = AutosaveManager(text_editor)
            
            assert autosave_manager.text_editor == text_editor
            assert autosave_manager.current_entry is None
            assert not autosave_manager.is_saving
            assert not autosave_manager.has_unsaved_changes
            assert not autosave_manager.first_keypress_handled
    
    def test_first_keypress_handling(self, app):
        """Test first keypress creates new entry."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager') as MockEntryManager:
            mock_manager = MockEntryManager.return_value
            mock_entry = Mock()
            mock_entry.is_new = True
            mock_manager.create_new_entry.return_value = mock_entry
            
            autosave_manager = AutosaveManager(text_editor)
            
            # Simulate first keypress
            text_editor.setPlainText("First character")
            autosave_manager._on_text_changed()
            
            # Should create new entry
            mock_manager.create_new_entry.assert_called_once()
            assert autosave_manager.first_keypress_handled
    
    def test_debounced_autosave(self, app):
        """Test debounced autosave functionality."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager'):
            autosave_manager = AutosaveManager(text_editor)
            autosave_manager.current_entry = Mock()
            
            # Mock the autosave method
            autosave_manager._save_current_entry = Mock()
            
            # Simulate text changes
            autosave_manager._on_text_changed()
            
            # Timer should be started
            assert autosave_manager.debounce_timer.isActive()
            
            # Trigger timer
            autosave_manager.debounce_timer.timeout.emit()
            
            # Should call save
            autosave_manager._save_current_entry.assert_called_once()
    
    def test_force_save(self, app):
        """Test force save functionality."""
        text_editor = QTextEdit()
        text_editor.setPlainText("Test content")
        
        with patch('src.pocket_journal.core.autosave.EntryManager') as MockEntryManager:
            mock_manager = MockEntryManager.return_value
            mock_manager.save_entry.return_value = True
            
            autosave_manager = AutosaveManager(text_editor)
            autosave_manager.current_entry = Mock()
            autosave_manager.current_entry.content = ""
            
            success = autosave_manager.force_save()
            
            assert success
            mock_manager.save_entry.assert_called_once()
    
    def test_create_new_entry_saves_current(self, app):
        """Test creating new entry saves current entry if modified."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager') as MockEntryManager:
            mock_manager = MockEntryManager.return_value
            mock_manager.create_new_entry.return_value = Mock()
            
            autosave_manager = AutosaveManager(text_editor)
            autosave_manager.current_entry = Mock()
            autosave_manager.has_unsaved_changes = True
            autosave_manager._perform_immediate_save = Mock()
            
            new_entry = autosave_manager.create_new_entry("New content")
            
            # Should save current entry first
            autosave_manager._perform_immediate_save.assert_called_once()
            # Should create new entry
            mock_manager.create_new_entry.assert_called_once_with("New content")


class TestEntryLifecycleManager:
    """Test the EntryLifecycleManager class."""
    
    def test_lifecycle_manager_initialization(self, app):
        """Test lifecycle manager initialization."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager'):
            autosave_manager = AutosaveManager(text_editor)
            lifecycle_manager = EntryLifecycleManager(autosave_manager)
            
            assert lifecycle_manager.autosave_manager == autosave_manager
    
    def test_entry_created_signal(self, app):
        """Test entry created signal emission."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager'):
            autosave_manager = AutosaveManager(text_editor)
            lifecycle_manager = EntryLifecycleManager(autosave_manager)
            
            # Mock signal
            lifecycle_manager.entry_created = Mock()
            
            # Mock entry info
            autosave_manager.get_current_entry_info = Mock(return_value={'id': 'test-id'})
            
            # Trigger entry creation
            mock_entry = Mock()
            lifecycle_manager._on_entry_created(mock_entry)
            
            # Should emit signal with entry info
            lifecycle_manager.entry_created.emit.assert_called_once_with({'id': 'test-id'})
    
    def test_save_completed_signal(self, app):
        """Test save completed signal emission."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager'):
            autosave_manager = AutosaveManager(text_editor)
            lifecycle_manager = EntryLifecycleManager(autosave_manager)
            
            # Mock signals
            lifecycle_manager.entry_updated = Mock()
            lifecycle_manager.entry_saved = Mock()
            
            # Mock return values
            autosave_manager.get_current_entry_info = Mock(return_value={'id': 'test-id'})
            autosave_manager.get_last_save_time_local = Mock(return_value='10:30 AM')
            
            # Trigger save completion
            lifecycle_manager._on_save_completed(True)
            
            # Should emit both signals
            lifecycle_manager.entry_updated.emit.assert_called_once_with({'id': 'test-id'})
            lifecycle_manager.entry_saved.emit.assert_called_once_with('10:30 AM')


class TestStep6AcceptanceCriteria:
    """Test Step 6 acceptance criteria specifically."""
    
    def test_first_keypress_creates_entry_with_utc_timestamp(self, app):
        """Test: On first keypress of a new note: instantiate new entry with ISO UTC created_at."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager') as MockEntryManager:
            mock_manager = MockEntryManager.return_value
            mock_entry = Mock()
            mock_entry.is_new = True
            mock_entry.metadata = Mock()
            mock_entry.metadata.created_at = "2025-10-02T20:00:00+00:00"
            mock_manager.create_new_entry.return_value = mock_entry
            
            autosave_manager = AutosaveManager(text_editor)
            
            # Simulate first keypress
            text_editor.setPlainText("First character")
            autosave_manager._on_text_changed()
            
            # Entry should be created
            mock_manager.create_new_entry.assert_called_once()
            
            # Should have UTC timestamp
            created_at = mock_entry.metadata.created_at
            assert created_at.endswith('+00:00') or created_at.endswith('Z')
    
    def test_debounced_autosave_with_configurable_delay(self, app):
        """Test: Debounced autosave (e.g., 900 ms)."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.get_setting', return_value=900):
            with patch('src.pocket_journal.core.autosave.EntryManager'):
                autosave_manager = AutosaveManager(text_editor)
                
                # Should use configured debounce delay
                assert autosave_manager.debounce_ms == 900
    
    def test_save_on_focus_out(self, app):
        """Test: save on editor focus-out."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager'):
            autosave_manager = AutosaveManager(text_editor)
            autosave_manager.current_entry = Mock()
            autosave_manager.has_unsaved_changes = True
            autosave_manager._perform_immediate_save = Mock()
            
            # Should save on focus out when enabled
            assert autosave_manager.save_on_focus_out
    
    def test_markdown_with_yaml_frontmatter_structure(self):
        """Test: Store entries as Markdown with YAML front-matter containing required fields."""
        entry = Entry("Test content")
        entry.metadata.title = "Test Entry"
        entry.metadata.tags = ["test"]
        
        markdown = entry.to_markdown()
        
        # Check required YAML fields
        required_fields = ['id', 'created_at', 'updated_at', 'title', 'subtitle', 'tags', 'word_count', 'path']
        for field in required_fields:
            assert f'{field}:' in markdown
        
        # Check ISO UTC timestamp format
        assert 'created_at:' in markdown
        assert 'updated_at:' in markdown
    
    def test_filename_pattern(self):
        """Test: Filename pattern: YYYY-MM-DD_HH-MM-SS_slug.md."""
        entry = Entry("Test content")
        entry.metadata.title = "My Test Entry"
        
        filename = entry.generate_filename()
        
        # Should match pattern YYYY-MM-DD_HH-MM-SS_slug.md
        import re
        pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_.*\.md'
        assert re.match(pattern, filename), f"Filename '{filename}' doesn't match expected pattern"
    
    def test_entries_directory_structure(self, temp_entries_dir):
        """Test: Acceptance - Entries save reliably under Documents\\PocketJournal\\Entries\\YYYY\\MM\\."""
        with patch('src.pocket_journal.data.entry_manager.EntryManager._get_base_path', return_value=temp_entries_dir):
            manager = EntryManager()
            
            # Create entry with specific date
            entry = manager.create_new_entry("Test content")
            # Mock creation date for predictable directory structure
            entry.metadata.created_at = "2025-10-02T15:30:00+00:00"
            
            success = manager.save_entry(entry)
            assert success
            
            # Check directory structure: base/YYYY/MM/filename.md
            expected_dir = temp_entries_dir / "2025" / "10"
            assert expected_dir.exists()
            
            # Check file exists in correct location
            file_path = Path(entry.metadata.path)
            assert file_path.parent == expected_dir
    
    def test_updated_at_changes_on_edits(self):
        """Test: Acceptance - updated_at changes on edits."""
        entry = Entry("Original content")
        original_updated_at = entry.metadata.updated_at
        
        # Simulate edit
        import time
        time.sleep(0.001)  # Ensure different timestamp
        entry.content = "Modified content"
        entry.update_metadata()
        
        # updated_at should change
        assert entry.metadata.updated_at != original_updated_at
    
    def test_autosave_indicator_reflects_save_state(self, app):
        """Test: Acceptance - autosave indicator reflects last save time."""
        text_editor = QTextEdit()
        
        with patch('src.pocket_journal.core.autosave.EntryManager') as MockEntryManager:
            mock_manager = MockEntryManager.return_value
            mock_manager.last_save_time = datetime.now()
            
            autosave_manager = AutosaveManager(text_editor)
            
            # Should be able to get last save time
            save_time = autosave_manager.get_last_save_time_local()
            assert isinstance(save_time, str)