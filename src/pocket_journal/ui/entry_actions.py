"""
Entry actions menu and functionality for PocketJournal.
Provides per-entry actions: View in folder, Rename, Duplicate, Export, Delete.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from PySide6.QtWidgets import (
    QMenu, QWidget, QFileDialog, QMessageBox, QInputDialog, 
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QProgressBar, QApplication
)
from PySide6.QtCore import QObject, Signal, QTimer, Qt
from PySide6.QtGui import QAction, QIcon

from ..data.entry_manager import Entry, EntryManager
from ..settings import get_setting, set_setting
from ..utils.file_utils import sanitize_filename, ensure_directory_exists


class UndoToastWidget(QFrame):
    """Toast notification with undo functionality for delete operations."""
    
    # Signals
    undo_requested = Signal()
    toast_expired = Signal()
    
    def __init__(self, message: str, timeout_ms: int = 10000, parent=None):
        """Initialize undo toast widget."""
        super().__init__(parent)
        
        self.timeout_ms = timeout_ms
        self.setup_ui(message)
        self.setup_timer()
    
    def setup_ui(self, message: str):
        """Setup the toast UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # Message label
        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.message_label)
        
        layout.addStretch()
        
        # Progress bar showing time remaining
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setMaximumWidth(80)
        self.progress_bar.setMaximumHeight(4)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Undo button
        self.undo_button = QPushButton("UNDO")
        self.undo_button.clicked.connect(self.undo_requested.emit)
        self.undo_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffeb3b;
                border: 1px solid #ffeb3b;
                padding: 4px 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 235, 59, 0.1);
            }
        """)
        layout.addWidget(self.undo_button)
        
        # Style the toast
        self.setStyleSheet("""
            UndoToastWidget {
                background-color: #424242;
                border-radius: 8px;
                border: 1px solid #616161;
            }
        """)
        
        self.setFixedHeight(40)
    
    def setup_timer(self):
        """Setup the countdown timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        
        self.start_time = datetime.now()
        self.timer.start(50)  # Update every 50ms for smooth progress
    
    def update_progress(self):
        """Update progress bar and handle timeout."""
        elapsed = (datetime.now() - self.start_time).total_seconds() * 1000
        progress = max(0, 100 - (elapsed / self.timeout_ms * 100))
        
        self.progress_bar.setValue(int(progress))
        
        if elapsed >= self.timeout_ms:
            self.timer.stop()
            self.toast_expired.emit()


class EntryActionsMenu(QMenu):
    """Context menu for entry actions."""
    
    # Signals
    view_in_folder_requested = Signal(str)  # file_path
    rename_requested = Signal(str, str)     # old_path, new_title
    duplicate_requested = Signal(str)       # source_path
    export_requested = Signal(str, str, str) # source_path, destination, format
    delete_requested = Signal(str)          # file_path
    
    def __init__(self, entry: Entry, parent=None):
        """Initialize entry actions menu."""
        super().__init__(parent)
        
        self.entry = entry
        self.entry_manager = EntryManager()
        self.setup_menu()
    
    def setup_menu(self):
        """Setup the context menu actions."""
        # View in folder
        view_action = QAction("📁 View in Folder", self)
        view_action.setToolTip("Open the folder containing this entry")
        view_action.triggered.connect(self._on_view_in_folder)
        self.addAction(view_action)
        
        self.addSeparator()
        
        # Rename
        rename_action = QAction("✏️ Rename Entry", self)
        rename_action.setToolTip("Rename this entry (updates filename and title)")
        rename_action.triggered.connect(self._on_rename)
        self.addAction(rename_action)
        
        # Duplicate
        duplicate_action = QAction("📄 Duplicate Entry", self)
        duplicate_action.setToolTip("Create a copy of this entry")
        duplicate_action.triggered.connect(self._on_duplicate)
        self.addAction(duplicate_action)
        
        self.addSeparator()
        
        # Export submenu
        export_menu = self.addMenu("📤 Export")
        export_menu.setToolTip("Export this entry to different formats")
        
        # Export as Markdown
        export_md_action = QAction("Export as Markdown (.md)", self)
        export_md_action.triggered.connect(lambda: self._on_export("markdown"))
        export_menu.addAction(export_md_action)
        
        # Export as Text
        export_txt_action = QAction("Export as Text (.txt)", self)
        export_txt_action.triggered.connect(lambda: self._on_export("text"))
        export_menu.addAction(export_txt_action)
        
        self.addSeparator()
        
        # Delete
        delete_action = QAction("🗑️ Delete Entry", self)
        delete_action.setToolTip("Delete this entry (with 10-second undo)")
        delete_action.triggered.connect(self._on_delete)
        self.addAction(delete_action)
    
    def _on_view_in_folder(self):
        """Handle view in folder action."""
        if not self.entry.metadata.path or not Path(self.entry.metadata.path).exists():
            QMessageBox.warning(self.parent(), "Entry Not Found", 
                              "The entry file could not be found on disk.")
            return
        
        file_path = str(Path(self.entry.metadata.path).resolve())
        self.view_in_folder_requested.emit(file_path)
    
    def _on_rename(self):
        """Handle rename entry action."""
        current_title = self.entry.metadata.title or "Untitled Entry"
        
        new_title, ok = QInputDialog.getText(
            self.parent(),
            "Rename Entry",
            "Enter new title:",
            text=current_title
        )
        
        if ok and new_title.strip():
            new_title = new_title.strip()
            if new_title != current_title:
                old_path = self.entry.metadata.path
                self.rename_requested.emit(old_path, new_title)
    
    def _on_duplicate(self):
        """Handle duplicate entry action."""
        if not self.entry.metadata.path:
            QMessageBox.warning(self.parent(), "Cannot Duplicate", 
                              "Cannot duplicate unsaved entry.")
            return
        
        source_path = self.entry.metadata.path
        self.duplicate_requested.emit(source_path)
    
    def _on_export(self, export_format: str):
        """Handle export entry action."""
        # Get default export directory
        data_dir = Path(get_setting("data_directory", str(Path.home() / "PocketJournal")))
        export_dir = data_dir / "Exports"
        ensure_directory_exists(export_dir)
        
        # Generate default filename
        if export_format == "markdown":
            ext = ".md"
        else:
            ext = ".txt"
        
        title = self.entry.metadata.title or "entry"
        safe_title = sanitize_filename(title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{safe_title}_{timestamp}{ext}"
        
        # Show save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent(),
            f"Export Entry as {export_format.title()}",
            str(export_dir / default_filename),
            f"{export_format.title()} Files (*{ext});;All Files (*)"
        )
        
        if file_path:
            source_path = self.entry.metadata.path
            self.export_requested.emit(source_path, file_path, export_format)
    
    def _on_delete(self):
        """Handle delete entry action."""
        if not self.entry.metadata.path:
            QMessageBox.warning(self.parent(), "Cannot Delete", 
                              "Cannot delete unsaved entry.")
            return
        
        # Confirm deletion
        title = self.entry.metadata.title or "this entry"
        reply = QMessageBox.question(
            self.parent(),
            "Delete Entry",
            f"Are you sure you want to delete '{title}'?\n\n"
            "You will have 10 seconds to undo this action.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            file_path = self.entry.metadata.path
            self.delete_requested.emit(file_path)


class EntryActionsManager(QObject):
    """Manages entry actions and undo functionality."""
    
    # Signals
    entry_renamed = Signal(str, str)        # old_path, new_path
    entry_duplicated = Signal(str)          # new_path
    entry_exported = Signal(str, str)       # source_path, destination
    entry_deleted = Signal(str)             # deleted_path
    entry_restored = Signal(str)            # restored_path
    show_toast = Signal(QWidget)            # toast_widget
    hide_toast = Signal()
    
    def __init__(self, parent=None):
        """Initialize entry actions manager."""
        super().__init__(parent)
        
        self.entry_manager = EntryManager()
        self.deleted_entries = {}  # path -> backup_data for undo
    
    def create_actions_menu(self, entry: Entry, parent_widget=None) -> EntryActionsMenu:
        """Create an actions menu for the given entry."""
        menu = EntryActionsMenu(entry, parent_widget)
        
        # Connect menu signals
        menu.view_in_folder_requested.connect(self.view_in_folder)
        menu.rename_requested.connect(self.rename_entry)
        menu.duplicate_requested.connect(self.duplicate_entry)
        menu.export_requested.connect(self.export_entry)
        menu.delete_requested.connect(self.delete_entry)
        
        return menu
    
    def view_in_folder(self, file_path: str):
        """Open file explorer and select the entry file."""
        try:
            file_path = Path(file_path).resolve()
            
            if sys.platform == "win32":
                # Windows - use explorer with /select
                subprocess.run(["explorer", "/select,", str(file_path)], check=True)
            elif sys.platform == "darwin":
                # macOS - use Finder
                subprocess.run(["open", "-R", str(file_path)], check=True)
            else:
                # Linux - open parent directory
                parent_dir = file_path.parent
                subprocess.run(["xdg-open", str(parent_dir)], check=True)
        
        except Exception as e:
            QMessageBox.warning(None, "Error Opening Folder", 
                              f"Could not open folder: {str(e)}")
    
    def rename_entry(self, old_path: str, new_title: str):
        """Rename an entry, updating both filename and metadata."""
        try:
            old_path = Path(old_path)
            if not old_path.exists():
                QMessageBox.warning(None, "File Not Found", 
                                  "The entry file could not be found.")
                return
            
            # Load entry to update metadata
            with open(old_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entry = Entry.from_markdown(content, str(old_path))
            
            # Update title in metadata
            entry.metadata.title = new_title
            entry.metadata.updated_at = datetime.now().isoformat()
            
            # Generate new filename
            new_filename = self._generate_safe_filename(new_title, old_path.suffix)
            new_path = old_path.parent / new_filename
            
            # Ensure new path is unique
            counter = 1
            base_path = new_path
            while new_path.exists() and new_path != old_path:
                stem = base_path.stem
                new_path = base_path.parent / f"{stem}_{counter}{base_path.suffix}"
                counter += 1
            
            # Write updated content to new file
            updated_content = entry.to_markdown()
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            # Remove old file if different
            if new_path != old_path:
                old_path.unlink()
            
            self.entry_renamed.emit(str(old_path), str(new_path))
            
        except Exception as e:
            QMessageBox.critical(None, "Rename Failed", 
                               f"Failed to rename entry: {str(e)}")
    
    def duplicate_entry(self, source_path: str):
        """Create a duplicate of an entry."""
        try:
            source_path = Path(source_path)
            if not source_path.exists():
                QMessageBox.warning(None, "File Not Found", 
                                  "The entry file could not be found.")
                return
            
            # Load source entry
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entry = Entry.from_markdown(content, str(source_path))
            
            # Create new entry with modified metadata
            new_entry = Entry(entry.content)
            new_entry.metadata.title = f"{entry.metadata.title} (Copy)" if entry.metadata.title else "Untitled Entry (Copy)"
            new_entry.metadata.tags = entry.metadata.tags.copy()
            
            # Generate unique filename
            duplicate_filename = self._generate_safe_filename(new_entry.metadata.title, ".md")
            duplicate_path = source_path.parent / duplicate_filename
            
            # Ensure unique path
            counter = 1
            base_path = duplicate_path
            while duplicate_path.exists():
                stem = base_path.stem
                duplicate_path = base_path.parent / f"{stem}_{counter}{base_path.suffix}"
                counter += 1
            
            # Set the path for the new entry
            new_entry.metadata.path = str(duplicate_path)
            
            # Save duplicate manually since EntryManager.save_entry has a different interface
            duplicate_content = new_entry.to_markdown()
            duplicate_path.write_text(duplicate_content, encoding='utf-8')
            
            self.entry_duplicated.emit(str(duplicate_path))
            
        except Exception as e:
            QMessageBox.critical(None, "Duplication Failed", 
                               f"Failed to duplicate entry: {str(e)}")
    
    def export_entry(self, source_path: str, destination: str, export_format: str):
        """Export an entry to the specified format and location."""
        try:
            source_path = Path(source_path)
            destination = Path(destination)
            
            if not source_path.exists():
                QMessageBox.warning(None, "File Not Found", 
                                  "The entry file could not be found.")
                return
            
            # Load entry
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entry = Entry.from_markdown(content, str(source_path))
            
            # Prepare export content based on format
            if export_format == "markdown":
                # Export with full markdown including front-matter
                export_content = entry.to_markdown()
            else:  # text format
                # Export only the content without front-matter
                export_content = entry.content
            
            # Ensure destination directory exists
            ensure_directory_exists(destination.parent)
            
            # Write export file
            with open(destination, 'w', encoding='utf-8') as f:
                f.write(export_content)
            
            self.entry_exported.emit(str(source_path), str(destination))
            
            QMessageBox.information(None, "Export Successful", 
                                  f"Entry exported to:\n{destination}")
            
        except Exception as e:
            QMessageBox.critical(None, "Export Failed", 
                               f"Failed to export entry: {str(e)}")
    
    def delete_entry(self, file_path: str):
        """Delete an entry with undo capability."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                QMessageBox.warning(None, "File Not Found", 
                                  "The entry file could not be found.")
                return
            
            # Read file content for backup
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Store backup data
            backup_data = {
                'content': content,
                'path': str(file_path),
                'timestamp': datetime.now()
            }
            self.deleted_entries[str(file_path)] = backup_data
            
            # Delete the file
            file_path.unlink()
            
            # Create and show undo toast
            title = "Entry deleted"
            toast = UndoToastWidget(title, timeout_ms=10000)
            toast.undo_requested.connect(lambda: self.restore_entry(str(file_path)))
            toast.toast_expired.connect(lambda: self._cleanup_backup(str(file_path)))
            
            self.show_toast.emit(toast)
            self.entry_deleted.emit(str(file_path))
            
        except Exception as e:
            QMessageBox.critical(None, "Delete Failed", 
                               f"Failed to delete entry: {str(e)}")
    
    def restore_entry(self, file_path: str):
        """Restore a deleted entry from backup."""
        try:
            if file_path not in self.deleted_entries:
                QMessageBox.warning(None, "Restore Failed", 
                                  "No backup found for this entry.")
                return
            
            backup_data = self.deleted_entries[file_path]
            file_path_obj = Path(file_path)
            
            # Ensure directory exists
            ensure_directory_exists(file_path_obj.parent)
            
            # Restore file
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(backup_data['content'])
            
            # Clean up backup
            del self.deleted_entries[file_path]
            
            self.hide_toast.emit()
            self.entry_restored.emit(file_path)
            
        except Exception as e:
            QMessageBox.critical(None, "Restore Failed", 
                               f"Failed to restore entry: {str(e)}")
    
    def _cleanup_backup(self, file_path: str):
        """Clean up backup data after timeout."""
        if file_path in self.deleted_entries:
            del self.deleted_entries[file_path]
        self.hide_toast.emit()
    
    def _generate_safe_filename(self, title: str, extension: str) -> str:
        """Generate a safe filename from title."""
        if not title.strip():
            title = "untitled_entry"
        
        # Sanitize title
        safe_title = sanitize_filename(title)
        
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{timestamp}_{safe_title}{extension}"


def open_data_folder():
    """Open the PocketJournal data folder in file explorer."""
    try:
        data_dir = Path(get_setting("data_directory", str(Path.home() / "PocketJournal")))
        ensure_directory_exists(data_dir)
        
        if sys.platform == "win32":
            subprocess.run(["explorer", str(data_dir)], check=True)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(data_dir)], check=True)
        else:
            subprocess.run(["xdg-open", str(data_dir)], check=True)
    
    except Exception as e:
        QMessageBox.warning(None, "Error Opening Folder", 
                          f"Could not open data folder: {str(e)}")