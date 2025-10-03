"""
Autosave system for PocketJournal entries.
Handles debounced saving, focus-out saves, and entry lifecycle.
"""

import time
from datetime import datetime, timezone
from typing import Optional, Callable
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QTextEdit

from ..data.entry_manager import Entry, EntryManager
from ..settings import get_setting


class AutosaveManager(QObject):
    """Manages autosave functionality with debouncing and focus handling."""
    
    # Signals
    save_started = Signal()
    save_completed = Signal(bool)  # success
    entry_created = Signal(Entry)  # when new entry is instantiated
    
    def __init__(self, text_editor: QTextEdit, parent=None):
        """Initialize autosave manager."""
        super().__init__(parent)
        
        self.text_editor = text_editor
        self.entry_manager = EntryManager()
        self.current_entry: Optional[Entry] = None
        
        # Autosave configuration
        self.debounce_ms = get_setting("autosave_debounce_ms", 900)
        self.save_on_focus_out = get_setting("save_on_focus_out", True)
        
        # Timers
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._perform_autosave)
        
        # State tracking
        self.is_saving = False
        self.has_unsaved_changes = False
        self.first_keypress_handled = False
        
        # Connect text editor signals
        self._connect_editor_signals()
    
    def _connect_editor_signals(self):
        """Connect text editor signals for autosave."""
        self.text_editor.textChanged.connect(self._on_text_changed)
        self.text_editor.focusOutEvent = self._wrap_focus_out_event(
            self.text_editor.focusOutEvent
        )
    
    def _wrap_focus_out_event(self, original_focus_out):
        """Wrap focus out event to trigger save."""
        def wrapped_focus_out(event):
            if self.save_on_focus_out and self.has_unsaved_changes:
                self._perform_immediate_save()
            original_focus_out(event)
        return wrapped_focus_out
    
    def _on_text_changed(self):
        """Handle text changes in editor."""
        # Check for first keypress on new entry
        if not self.first_keypress_handled and self.text_editor.toPlainText().strip():
            self._handle_first_keypress()
        
        # Mark as having unsaved changes
        self.has_unsaved_changes = True
        
        # Update current entry content
        if self.current_entry:
            self.current_entry.content = self.text_editor.toPlainText()
        
        # Start/restart debounce timer
        self.debounce_timer.stop()
        self.debounce_timer.start(self.debounce_ms)
    
    def _handle_first_keypress(self):
        """Handle first keypress of new note - instantiate entry."""
        if not self.current_entry or not self.current_entry.is_new:
            # Create new entry with current content
            content = self.text_editor.toPlainText()
            self.current_entry = self.entry_manager.create_new_entry(content)
            
            # Emit signal for UI updates
            self.entry_created.emit(self.current_entry)
            
            print(f"New entry created: {self.current_entry.metadata.id}")
            print(f"Created at: {self.current_entry.metadata.created_at}")
        
        self.first_keypress_handled = True
    
    def _perform_autosave(self):
        """Perform debounced autosave."""
        if not self.has_unsaved_changes or not self.current_entry:
            return
        
        self._save_current_entry()
    
    def _perform_immediate_save(self):
        """Perform immediate save (on focus out, etc.)."""
        if not self.current_entry:
            return
        
        # Cancel debounce timer
        self.debounce_timer.stop()
        self._save_current_entry()
    
    def _save_current_entry(self):
        """Save current entry to file system."""
        if self.is_saving or not self.current_entry:
            return
        
        self.is_saving = True
        self.save_started.emit()
        
        try:
            # Update entry content
            self.current_entry.content = self.text_editor.toPlainText()
            
            # Save entry
            success = self.entry_manager.save_entry(self.current_entry)
            
            if success:
                self.has_unsaved_changes = False
                print(f"Entry saved: {self.current_entry.metadata.path}")
            else:
                print("Failed to save entry")
            
            self.save_completed.emit(success)
            
        except Exception as e:
            print(f"Error during autosave: {e}")
            self.save_completed.emit(False)
        
        finally:
            self.is_saving = False
    
    def create_new_entry(self, content: str = ""):
        """Create new entry and reset autosave state."""
        # Save current entry if it has changes
        if self.current_entry and self.has_unsaved_changes:
            self._perform_immediate_save()
        
        # Create new entry
        self.current_entry = self.entry_manager.create_new_entry(content)
        
        # Reset state
        self.has_unsaved_changes = False
        self.first_keypress_handled = False
        
        # Update text editor
        self.text_editor.setPlainText(content)
        
        print(f"New entry created: {self.current_entry.metadata.id}")
        return self.current_entry
    
    def load_entry(self, file_path: str) -> bool:
        """Load existing entry."""
        # Save current entry if needed
        if self.current_entry and self.has_unsaved_changes:
            self._perform_immediate_save()
        
        # Load entry
        entry = self.entry_manager.load_entry(file_path)
        if not entry:
            return False
        
        self.current_entry = entry
        
        # Update text editor
        self.text_editor.setPlainText(entry.content)
        
        # Reset state
        self.has_unsaved_changes = False
        self.first_keypress_handled = True  # Existing entry
        
        print(f"Entry loaded: {entry.metadata.path}")
        return True
    
    def force_save(self) -> bool:
        """Force immediate save of current entry."""
        if not self.current_entry:
            return False
        
        self.debounce_timer.stop()
        
        # Update content
        self.current_entry.content = self.text_editor.toPlainText()
        
        # Force save
        success = self.entry_manager.save_entry(self.current_entry, force=True)
        
        if success:
            self.has_unsaved_changes = False
        
        return success
    
    def save_and_close(self) -> bool:
        """Save current entry before app close."""
        if self.current_entry and (self.has_unsaved_changes or self.current_entry.is_new):
            return self.force_save()
        return True
    
    def get_current_entry_info(self) -> dict:
        """Get current entry information for UI display."""
        if not self.current_entry:
            return {}
        
        # Convert UTC timestamps to local display
        created_utc = datetime.fromisoformat(
            self.current_entry.metadata.created_at.replace('Z', '+00:00')
        )
        updated_utc = datetime.fromisoformat(
            self.current_entry.metadata.updated_at.replace('Z', '+00:00')
        )
        
        # Format for US display
        created_local = created_utc.astimezone().strftime("%m/%d/%Y %I:%M %p")
        updated_local = updated_utc.astimezone().strftime("%m/%d/%Y %I:%M %p")
        
        return {
            'id': self.current_entry.metadata.id,
            'title': self.current_entry.metadata.title or "Untitled",
            'created_at_local': created_local,
            'updated_at_local': updated_local,
            'word_count': self.current_entry.metadata.word_count,
            'is_new': self.current_entry.is_new,
            'is_modified': self.current_entry.is_modified,
            'has_unsaved_changes': self.has_unsaved_changes,
            'file_path': self.current_entry.metadata.path
        }
    
    def get_last_save_time_local(self) -> str:
        """Get last save time in local US format."""
        if not self.entry_manager.last_save_time:
            return ""
        
        return self.entry_manager.last_save_time.strftime("%I:%M %p")
    
    def update_settings(self):
        """Update autosave settings from config."""
        self.debounce_ms = get_setting("autosave_debounce_ms", 900)
        self.save_on_focus_out = get_setting("save_on_focus_out", True)
        
        print(f"Autosave settings updated: debounce={self.debounce_ms}ms, save_on_focus_out={self.save_on_focus_out}")


class EntryLifecycleManager(QObject):
    """Manages entry lifecycle events and notifications."""
    
    # Signals
    entry_created = Signal(dict)  # entry info
    entry_updated = Signal(dict)  # entry info
    entry_saved = Signal(str)     # save time
    
    def __init__(self, autosave_manager: AutosaveManager, parent=None):
        """Initialize lifecycle manager."""
        super().__init__(parent)
        
        self.autosave_manager = autosave_manager
        
        # Connect autosave signals
        self.autosave_manager.entry_created.connect(self._on_entry_created)
        self.autosave_manager.save_completed.connect(self._on_save_completed)
    
    def _on_entry_created(self, entry: Entry):
        """Handle new entry creation."""
        entry_info = self.autosave_manager.get_current_entry_info()
        self.entry_created.emit(entry_info)
    
    def _on_save_completed(self, success: bool):
        """Handle save completion."""
        if success:
            entry_info = self.autosave_manager.get_current_entry_info()
            save_time = self.autosave_manager.get_last_save_time_local()
            
            self.entry_updated.emit(entry_info)
            self.entry_saved.emit(save_time)
    
    def get_entry_display_time(self) -> str:
        """Get current entry time for display."""
        entry_info = self.autosave_manager.get_current_entry_info()
        
        if not entry_info:
            return ""
        
        if entry_info.get('is_new'):
            return f"Created {entry_info.get('created_at_local', '')}"
        else:
            return f"Updated {entry_info.get('updated_at_local', '')}"