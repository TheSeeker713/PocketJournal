"""
Recent entries and search functionality for PocketJournal.

This module implements:
- Recent entries popover (hover over launcher)
- Search dialog (Ctrl+K)
- Fast in-memory search with preview
"""

import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QLineEdit, QListWidget, QListWidgetItem, QTextEdit,
    QSplitter, QFrame, QScrollArea, QApplication, QSizePolicy
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, QObject, Signal, QPropertyAnimation,
    QEasingCurve, QRect, QPoint, QSize, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPixmap, QPainterPath,
    QMouseEvent, QKeyEvent, QIcon, QFontMetrics, QPalette
)

from ..data.entry_manager import EntryManager, Entry
from ..settings import get_setting

logger = logging.getLogger(__name__)


class RecentEntryItem(QWidget):
    """Individual recent entry item widget."""
    
    entry_clicked = Signal(str)  # file_path
    
    def __init__(self, entry_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.entry_info = entry_info
        self.file_path = entry_info.get('file_path', '')
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the entry item UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        # Title
        title = self.entry_info.get('title', 'Untitled')
        if not title.strip():
            title = 'Untitled'
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333; background: transparent;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Timestamp (convert from UTC to local)
        try:
            created_at = self.entry_info.get('created_at', '')
            if created_at:
                utc_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                local_time = utc_time.astimezone()
                time_str = local_time.strftime("%m/%d/%y %I:%M %p")
            else:
                time_str = "Unknown time"
        except:
            time_str = "Unknown time"
            
        time_label = QLabel(time_str)
        time_label.setFont(QFont("Segoe UI", 8))
        time_label.setStyleSheet("color: #666; background: transparent;")
        layout.addWidget(time_label)
        
        # Word count if available
        word_count = self.entry_info.get('word_count', 0)
        if word_count > 0:
            count_label = QLabel(f"{word_count} words")
            count_label.setFont(QFont("Segoe UI", 8))
            count_label.setStyleSheet("color: #888; background: transparent;")
            layout.addWidget(count_label)
        
        # Make clickable
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
            }
            QWidget:hover {
                background-color: #e9ecef;
                border-color: #007bff;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press to open entry."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.entry_clicked.emit(self.file_path)
            event.accept()
        super().mousePressEvent(event)


class RecentEntriesPopover(QWidget):
    """Popover showing recent entries on launcher hover."""
    
    entry_selected = Signal(str)  # file_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entry_manager = EntryManager()
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        """Configure window properties."""
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(280, 320)
        
    def setup_ui(self):
        """Setup the popover UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Background frame
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        
        # Header
        header = QLabel("Recent Entries")
        header.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        header.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 1px solid #e9ecef;
                border-radius: 8px 8px 0 0;
                padding: 8px 12px;
                color: #495057;
            }
        """)
        frame_layout.addWidget(header)
        
        # Scroll area for entries
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                width: 8px;
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar::handle:vertical {
                background-color: #ced4da;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #adb5bd;
            }
        """)
        
        # Container for entry items
        self.entries_widget = QWidget()
        self.entries_layout = QVBoxLayout(self.entries_widget)
        self.entries_layout.setContentsMargins(4, 4, 4, 4)
        self.entries_layout.setSpacing(4)
        
        self.scroll_area.setWidget(self.entries_widget)
        frame_layout.addWidget(self.scroll_area)
        
        layout.addWidget(self.frame)
        
    def load_recent_entries(self):
        """Load and display recent entries."""
        # Clear existing items
        for i in reversed(range(self.entries_layout.count())):
            child = self.entries_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get recent entries
        recent_entries = self.entry_manager.get_recent_entries(limit=10)
        
        if not recent_entries:
            # Show "no entries" message
            no_entries = QLabel("No entries found")
            no_entries.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_entries.setStyleSheet("color: #666; padding: 20px;")
            self.entries_layout.addWidget(no_entries)
        else:
            # Add entry items
            for entry_info in recent_entries:
                item = RecentEntryItem(entry_info)
                item.entry_clicked.connect(self.entry_selected.emit)
                self.entries_layout.addWidget(item)
        
        # Add stretch to push items to top
        self.entries_layout.addStretch()
        
    def show_near_launcher(self, launcher_pos: QPoint, launcher_size: QSize):
        """Show popover positioned near the launcher."""
        self.load_recent_entries()
        
        # Calculate position (to the right of launcher)
        x = launcher_pos.x() + launcher_size.width() + 10
        y = launcher_pos.y()
        
        # Ensure popover stays on screen
        screen = QApplication.primaryScreen().availableGeometry()
        if x + self.width() > screen.right():
            x = launcher_pos.x() - self.width() - 10  # Show to left instead
        if y + self.height() > screen.bottom():
            y = screen.bottom() - self.height()
        if y < screen.top():
            y = screen.top()
            
        self.move(x, y)
        self.show()
        self.raise_()


class SearchResultItem(QWidget):
    """Individual search result item widget."""
    
    result_clicked = Signal(str)  # file_path
    
    def __init__(self, result_info: Dict[str, Any], query: str = "", parent=None):
        super().__init__(parent)
        self.result_info = result_info
        self.query = query
        self.file_path = result_info.get('file_path', '')
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the result item UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Title with highlighting
        title = self.result_info.get('title', 'Untitled')
        if not title.strip():
            title = 'Untitled'
        
        title_label = QLabel(self.highlight_text(title, self.query))
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333; background: transparent;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Preview text with highlighting
        preview = self.result_info.get('preview', '')
        if preview:
            preview_label = QLabel(self.highlight_text(preview, self.query))
            preview_label.setFont(QFont("Segoe UI", 9))
            preview_label.setStyleSheet("color: #555; background: transparent;")
            preview_label.setWordWrap(True)
            preview_label.setMaximumHeight(60)  # Limit height
            layout.addWidget(preview_label)
        
        # Metadata line (date + word count)
        meta_parts = []
        
        # Date
        try:
            created_at = self.result_info.get('created_at', '')
            if created_at:
                utc_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                local_time = utc_time.astimezone()
                meta_parts.append(local_time.strftime("%m/%d/%y"))
        except:
            pass
            
        # Word count
        word_count = self.result_info.get('word_count', 0)
        if word_count > 0:
            meta_parts.append(f"{word_count} words")
            
        if meta_parts:
            meta_text = " • ".join(meta_parts)
            meta_label = QLabel(meta_text)
            meta_label.setFont(QFont("Segoe UI", 8))
            meta_label.setStyleSheet("color: #888; background: transparent;")
            layout.addWidget(meta_label)
        
        # Make clickable
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 4px;
            }
            QWidget:hover {
                background-color: #e9ecef;
                border-color: #007bff;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def highlight_text(self, text: str, query: str) -> str:
        """Highlight query terms in text."""
        if not query or not text:
            return text
            
        # Split query into words
        query_words = query.strip().split()
        if not query_words:
            return text
            
        # Escape HTML in text
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Highlight each query word (case insensitive)
        for word in query_words:
            if len(word) > 1:  # Only highlight words with 2+ characters
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                text = pattern.sub(f'<span style="background-color: #fff3cd; color: #856404;">{word}</span>', text)
        
        return text
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press to open entry."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.result_clicked.emit(self.file_path)
            event.accept()
        super().mousePressEvent(event)


class FastSearchEngine(QObject):
    """Fast in-memory search engine for entries."""
    
    search_completed = Signal(list)  # search results
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entry_manager = EntryManager()
        
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Perform fast search across entries."""
        if not query.strip():
            return []
        
        start_time = time.time()
        results = []
        query_lower = query.lower().strip()
        query_words = query_lower.split()
        
        try:
            # Search through entry files
            for md_file in self.entry_manager.base_path.rglob("*.md"):
                try:
                    # Read file content
                    content = md_file.read_text(encoding='utf-8')
                    
                    # Split front-matter and body
                    if content.startswith('---\n'):
                        parts = content.split('---\n', 2)
                        if len(parts) >= 3:
                            front_matter = parts[1]
                            body = parts[2]
                        else:
                            continue
                    else:
                        continue
                    
                    # Parse metadata from front-matter
                    metadata = {}
                    for line in front_matter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            metadata[key] = value
                    
                    # Search in title and first ~1000 chars of body
                    title = metadata.get('title', '')
                    search_text = f"{title} {body[:1000]}".lower()
                    
                    # Calculate relevance score
                    score = 0
                    
                    # Exact phrase match gets highest score
                    if query_lower in search_text:
                        score += 100
                    
                    # Title matches get higher score
                    if title and query_lower in title.lower():
                        score += 50
                    
                    # Individual word matches
                    for word in query_words:
                        if len(word) > 1:  # Skip single characters
                            word_count = search_text.count(word)
                            score += word_count * 10
                    
                    # Only include results with positive score
                    if score > 0:
                        # Create preview text (first match context)
                        preview = self._extract_preview(body, query_words)
                        
                        result = {
                            'file_path': str(md_file),
                            'title': metadata.get('title', 'Untitled'),
                            'created_at': metadata.get('created_at', ''),
                            'word_count': int(metadata.get('word_count', 0)),
                            'preview': preview,
                            'score': score
                        }
                        results.append(result)
                        
                except Exception as e:
                    logger.debug(f"Error searching file {md_file}: {e}")
                    continue
                    
                # Stop if we have enough results and search is taking too long
                if len(results) >= limit * 2 and (time.time() - start_time) > 0.1:
                    break
        
        except Exception as e:
            logger.error(f"Search error: {e}")
        
        # Sort by relevance score and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        results = results[:limit]
        
        search_time = time.time() - start_time
        logger.debug(f"Search completed in {search_time:.3f}s with {len(results)} results")
        
        return results
    
    def _extract_preview(self, text: str, query_words: List[str]) -> str:
        """Extract preview text around query matches."""
        if not query_words:
            return text[:150] + "..." if len(text) > 150 else text
        
        # Find first match
        text_lower = text.lower()
        first_match_pos = len(text)
        
        for word in query_words:
            if len(word) > 1:
                pos = text_lower.find(word)
                if pos != -1 and pos < first_match_pos:
                    first_match_pos = pos
        
        if first_match_pos == len(text):
            # No matches found, return beginning
            return text[:150] + "..." if len(text) > 150 else text
        
        # Extract context around match
        start = max(0, first_match_pos - 50)
        end = min(len(text), first_match_pos + 100)
        
        # Try to break at word boundaries
        if start > 0:
            space_pos = text.find(' ', start)
            if space_pos != -1 and space_pos < start + 20:
                start = space_pos + 1
        
        if end < len(text):
            space_pos = text.rfind(' ', end - 20, end)
            if space_pos != -1:
                end = space_pos
        
        preview = text[start:end].strip()
        
        # Add ellipsis
        if start > 0:
            preview = "..." + preview
        if end < len(text):
            preview = preview + "..."
            
        return preview


class SearchDialog(QDialog):
    """Search dialog for finding entries."""
    
    entry_selected = Signal(str)  # file_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_engine = FastSearchEngine()
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        
        self.setup_window()
        self.setup_ui()
        self.setup_connections()
        
    def setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Search Entries")
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
    def setup_ui(self):
        """Setup the search dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search entries... (title, content)")
        self.search_input.setFont(QFont("Segoe UI", 11))
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        layout.addWidget(self.search_input)
        
        # Status label
        self.status_label = QLabel("Enter search terms above")
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet("color: #666; padding: 4px 0;")
        layout.addWidget(self.status_label)
        
        # Results area
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
            }
        """)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(4, 4, 4, 4)
        self.results_layout.setSpacing(4)
        
        self.results_scroll.setWidget(self.results_widget)
        layout.addWidget(self.results_scroll)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.setFont(QFont("Segoe UI", 9))
        self.close_button.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
        """)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def setup_connections(self):
        """Setup signal connections."""
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.close_button.clicked.connect(self.close)
        
    def _on_search_text_changed(self, text: str):
        """Handle search text changes with debouncing."""
        # Stop previous search
        self.search_timer.stop()
        
        if text.strip():
            # Start search after delay
            self.search_timer.start(300)  # 300ms delay
            self.status_label.setText("Searching...")
        else:
            self._clear_results()
            self.status_label.setText("Enter search terms above")
    
    def _perform_search(self):
        """Perform the actual search."""
        query = self.search_input.text().strip()
        if not query:
            return
        
        start_time = time.time()
        results = self.search_engine.search(query, limit=20)
        search_time = (time.time() - start_time) * 1000  # Convert to ms
        
        self._display_results(results, query, search_time)
        
    def _display_results(self, results: List[Dict[str, Any]], query: str, search_time: float):
        """Display search results."""
        self._clear_results()
        
        # Update status
        if results:
            self.status_label.setText(f"Found {len(results)} results in {search_time:.0f}ms")
        else:
            self.status_label.setText("No results found")
        
        # Add result items
        for result in results:
            item = SearchResultItem(result, query)
            item.result_clicked.connect(self._on_result_clicked)
            self.results_layout.addWidget(item)
        
        # Add stretch to push results to top
        self.results_layout.addStretch()
        
    def _clear_results(self):
        """Clear current search results."""
        for i in reversed(range(self.results_layout.count())):
            child = self.results_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
    def _on_result_clicked(self, file_path: str):
        """Handle result click."""
        self.entry_selected.emit(file_path)
        self.close()
        
    def showEvent(self, event):
        """Handle dialog show event."""
        super().showEvent(event)
        # Focus search input and clear it
        self.search_input.clear()
        self.search_input.setFocus()
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)