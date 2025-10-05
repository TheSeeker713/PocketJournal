"""
Help Center for PocketJournal.

This module provides a comprehensive help system with markdown rendering,
table of contents, and helper actions.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTextBrowser,
    QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QFrame,
    QScrollArea, QWidget, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QUrl, QTimer
from PySide6.QtGui import QFont, QDesktopServices, QKeySequence, QShortcut

from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.anchors import anchors_plugin

from ..settings import get_setting, set_setting
from ..app_meta import APP_NAME, get_version_string
from .entry_actions import open_data_folder
from .settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)


class HelpContentRenderer:
    """Renders markdown help content with enhanced features."""
    
    def __init__(self):
        self.md = MarkdownIt("commonmark", {"breaks": True, "linkify": True})
        self.md.use(front_matter_plugin)
        self.md.use(anchors_plugin)
        
        # CSS for help content
        self.css_style = """
        <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: none;
            margin: 0;
            padding: 20px;
            background-color: #fafafa;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
            font-size: 28px;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 22px;
        }
        
        h3 {
            color: #2c3e50;
            margin-top: 25px;
            font-size: 18px;
        }
        
        h4 {
            color: #7f8c8d;
            margin-top: 20px;
            font-size: 16px;
        }
        
        p {
            margin-bottom: 16px;
            text-align: justify;
        }
        
        code {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            padding: 2px 6px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 90%;
            color: #c7254e;
        }
        
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }
        
        pre code {
            background: none;
            border: none;
            padding: 0;
            color: #333;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 14px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 12px 8px;
            text-align: left;
        }
        
        th {
            background-color: #f2f2f2;
            font-weight: bold;
            color: #2c3e50;
        }
        
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        ul, ol {
            padding-left: 25px;
            margin-bottom: 16px;
        }
        
        li {
            margin-bottom: 8px;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            background-color: #f8f9fa;
            margin: 20px 0;
            padding: 16px 20px;
            font-style: italic;
        }
        
        .tip {
            background-color: #e8f4fd;
            border: 1px solid #bee5eb;
            border-radius: 6px;
            padding: 16px;
            margin: 20px 0;
        }
        
        .warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 16px;
            margin: 20px 0;
        }
        
        .error {
            background-color: #f8d7da;
            border: 1px solid #f1556c;
            border-radius: 6px;
            padding: 16px;
            margin: 20px 0;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:hover {
            color: #2980b9;
            text-decoration: underline;
        }
        
        .helper-link {
            background-color: #e3f2fd;
            border: 2px solid #2196f3;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 10px 0;
            display: inline-block;
            color: #1976d2;
            font-weight: bold;
            text-decoration: none;
            cursor: pointer;
        }
        
        .helper-link:hover {
            background-color: #bbdefb;
            border-color: #1976d2;
        }
        
        .keyboard-key {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 3px;
            padding: 2px 8px;
            font-family: monospace;
            font-size: 12px;
            box-shadow: 0 1px 0 rgba(0,0,0,0.2);
            display: inline-block;
            margin: 0 2px;
        }
        
        .status-good { color: #28a745; font-weight: bold; }
        .status-warning { color: #ffc107; font-weight: bold; }
        .status-error { color: #dc3545; font-weight: bold; }
        </style>
        """
    
    def render_markdown(self, content: str) -> str:
        """Render markdown content to HTML with styling."""
        # Convert markdown to HTML
        html_content = self.md.render(content)
        
        # Enhance content with helper links and special formatting
        html_content = self._process_helper_links(html_content)
        html_content = self._process_keyboard_shortcuts(html_content)
        html_content = self._process_status_indicators(html_content)
        
        # Wrap in styled HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>PocketJournal Help</title>
            {self.css_style}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return full_html
    
    def _process_helper_links(self, html: str) -> str:
        """Process helper action links."""
        # Define helper actions
        helpers = {
            "copy-data-folder-path": "Copy Data Folder Path",
            "open-data-folder": "Open Data Folder",
            "reset-formatting": "Reset Formatting to Defaults"
        }
        
        for action, text in helpers.items():
            # Replace markdown-style links with HTML helper links
            link_pattern = f'<a href="#{action}">{text}</a>'
            helper_html = f'<a href="helper://{action}" class="helper-link">{text}</a>'
            html = html.replace(link_pattern, helper_html)
        
        return html
    
    def _process_keyboard_shortcuts(self, html: str) -> str:
        """Process keyboard shortcut formatting."""
        import re
        
        # Pattern to match `Key+Combination`
        kbd_pattern = r'`([^`]+\+[^`]+)`'
        
        def replace_kbd(match):
            keys = match.group(1)
            # Split by + and wrap each key
            key_parts = [f'<span class="keyboard-key">{key.strip()}</span>' 
                        for key in keys.split('+')]
            return '+'.join(key_parts)
        
        return re.sub(kbd_pattern, replace_kbd, html)
    
    def _process_status_indicators(self, html: str) -> str:
        """Process status indicators like checkmarks and warnings."""
        # Replace common status patterns
        html = html.replace('✅', '<span class="status-good">✅</span>')
        html = html.replace('⚠️', '<span class="status-warning">⚠️</span>')
        html = html.replace('❌', '<span class="status-error">❌</span>')
        html = html.replace('🔧', '<span class="status-warning">🔧</span>')
        
        return html


class HelpTableOfContents(QTreeWidget):
    """Table of contents for help navigation."""
    
    section_selected = Signal(str)  # section filename
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setIndentation(20)
        self.setFixedWidth(250)
        
        # Define help structure
        self.help_sections = [
            ("quick-start", "Quick Start", "Get started with PocketJournal basics"),
            ("smart-formatting", "Smart Formatting", "Automatic text formatting rules"),
            ("navigation-search", "Navigation & Search", "Finding and organizing entries"),
            ("files-exports", "Files & Exports", "Managing your data and exports"),
            ("settings", "Settings", "Customizing your experience"),
            ("privacy", "Privacy", "Data security and privacy practices"),
            ("shortcuts", "Shortcuts", "Complete keyboard reference"),
            ("troubleshooting", "Troubleshooting", "Common issues and solutions"),
        ]
        
        self.setup_toc()
        
        # Connect selection signal
        self.itemClicked.connect(self._on_item_clicked)
    
    def setup_toc(self):
        """Setup the table of contents tree."""
        self.clear()
        
        # Add title item
        title_item = QTreeWidgetItem([f"{APP_NAME} Help"])
        title_item.setFont(0, QFont("Arial", 12, QFont.Weight.Bold))
        title_item.setData(0, Qt.ItemDataRole.UserRole, None)
        self.addTopLevelItem(title_item)
        title_item.setExpanded(True)
        
        # Add sections
        for section_id, title, description in self.help_sections:
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.ItemDataRole.UserRole, section_id)
            item.setToolTip(0, description)
            title_item.addChild(item)
        
        # Select first section by default
        if self.help_sections:
            first_section = title_item.child(0)
            self.setCurrentItem(first_section)
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item selection."""
        section_id = item.data(0, Qt.ItemDataRole.UserRole)
        if section_id:
            self.section_selected.emit(section_id)
    
    def select_section(self, section_id: str):
        """Programmatically select a section."""
        # Find the item with matching section_id
        root = self.topLevelItem(0)
        if root:
            for i in range(root.childCount()):
                item = root.child(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == section_id:
                    self.setCurrentItem(item)
                    break


class HelpContentBrowser(QTextBrowser):
    """Enhanced text browser for help content."""
    
    helper_action_triggered = Signal(str)  # action name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.renderer = HelpContentRenderer()
        self.help_dir = Path(__file__).parent.parent.parent / "help"
        
        # Configure browser
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)
        
        # Connect link clicking
        self.anchorClicked.connect(self._handle_link_click)
        
        # Set up search functionality
        self.search_text = ""
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
    
    def load_section(self, section_id: str):
        """Load a help section by ID."""
        try:
            section_file = self.help_dir / f"{section_id}.md"
            
            if not section_file.exists():
                self._show_section_not_found(section_id)
                return
            
            # Read markdown content
            with open(section_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Render to HTML
            html_content = self.renderer.render_markdown(markdown_content)
            
            # Set content
            self.setHtml(html_content)
            
            # Scroll to top
            self.moveCursor(self.textCursor().Start)
            
            logger.debug(f"Loaded help section: {section_id}")
            
        except Exception as e:
            logger.error(f"Failed to load help section {section_id}: {e}")
            self._show_error(f"Failed to load help section: {e}")
    
    def _handle_link_click(self, url: QUrl):
        """Handle link clicks in help content."""
        url_str = url.toString()
        
        if url_str.startswith("helper://"):
            # Helper action link
            action = url_str.replace("helper://", "")
            self.helper_action_triggered.emit(action)
        
        elif url_str.startswith("http://") or url_str.startswith("https://"):
            # External link
            QDesktopServices.openUrl(url)
        
        elif url_str.startswith("#"):
            # Internal anchor link
            anchor = url_str[1:]
            self._scroll_to_anchor(anchor)
        
        else:
            # Treat as section reference
            section_id = url_str.replace(".md", "")
            self.load_section(section_id)
    
    def _scroll_to_anchor(self, anchor: str):
        """Scroll to an anchor within the current page."""
        # Find the anchor in the document
        cursor = self.document().find(f'id="{anchor}"')
        if not cursor.isNull():
            self.setTextCursor(cursor)
            self.ensureCursorVisible()
    
    def _show_section_not_found(self, section_id: str):
        """Show error for missing section."""
        error_html = f"""
        <h1>Section Not Found</h1>
        <p>The help section <code>{section_id}</code> could not be found.</p>
        <p>Available sections:</p>
        <ul>
            <li>quick-start</li>
            <li>smart-formatting</li>
            <li>navigation-search</li>
            <li>files-exports</li>
            <li>settings</li>
            <li>privacy</li>
            <li>shortcuts</li>
            <li>troubleshooting</li>
        </ul>
        """
        self.setHtml(self.renderer.css_style + error_html)
    
    def _show_error(self, message: str):
        """Show error message in browser."""
        error_html = f"""
        <h1>Error</h1>
        <p>{message}</p>
        <p>Please try refreshing the help content or contact support.</p>
        """
        self.setHtml(self.renderer.css_style + error_html)
    
    def search_in_content(self, query: str):
        """Search within the current content."""
        self.search_text = query
        self.search_timer.start(300)  # Debounce search
    
    def _perform_search(self):
        """Perform the actual search."""
        if not self.search_text:
            return
        
        # Use Qt's built-in find functionality
        if self.find(self.search_text):
            # Found - text is automatically highlighted
            pass
        else:
            # Not found - try from beginning
            cursor = self.textCursor()
            cursor.movePosition(cursor.Start)
            self.setTextCursor(cursor)
            self.find(self.search_text)


class HelpCenter(QDialog):
    """
    Comprehensive help center with table of contents and markdown rendering.
    
    Step 11 Requirements:
    - Non-blocking help modal with TOC
    - Markdown content rendering with minimal CSS
    - Helper action links (copy data folder, open folder, reset formatting)
    - Full keyboard navigation (F1 to open, fully navigable)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_connections()
        
        # Set dialog properties
        self.setWindowTitle(f"{APP_NAME} Help Center")
        self.setModal(False)  # Non-blocking as required
        self.resize(1000, 700)
        
        # Load default section
        self.load_initial_section()
        
        logger.debug("Help center initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("QFrame { background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; }")
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel(f"{APP_NAME} Help Center")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50; background: none; border: none;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Version info
        version_label = QLabel(f"Version {get_version_string()}")
        version_label.setStyleSheet("color: #6c757d; background: none; border: none; font-size: 12px;")
        header_layout.addWidget(version_label)
        
        layout.addWidget(header_frame)
        
        # Main content area
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Table of contents
        self.toc = HelpTableOfContents()
        main_splitter.addWidget(self.toc)
        
        # Content browser
        self.content_browser = HelpContentBrowser()
        main_splitter.addWidget(self.content_browser)
        
        # Set splitter proportions (25% TOC, 75% content)
        main_splitter.setSizes([250, 750])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        
        layout.addWidget(main_splitter)
        
        # Footer with about and close buttons
        footer_layout = QHBoxLayout()
        
        # About button on the left
        self.about_btn = QPushButton("About")
        self.about_btn.setToolTip("Show application information")
        self.about_btn.clicked.connect(self.show_about)
        footer_layout.addWidget(self.about_btn)
        
        footer_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.setDefault(True)
        self.close_btn.clicked.connect(self.close)
        footer_layout.addWidget(self.close_btn)
        
        layout.addLayout(footer_layout)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts for full keyboard navigation."""
        # F1 to close (since F1 opens, F1 again should close)
        f1_shortcut = QShortcut(QKeySequence("F1"), self)
        f1_shortcut.activated.connect(self.close)
        
        # Escape to close
        esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        esc_shortcut.activated.connect(self.close)
        
        # Ctrl+F for find in page
        find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        find_shortcut.activated.connect(self.open_find_dialog)
        
        # Number keys for section navigation
        for i in range(8):  # 8 sections
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self.navigate_to_section(idx))
        
        # Tab and Shift+Tab for navigation
        self.setTabOrder(self.toc, self.content_browser)
        self.setTabOrder(self.content_browser, self.close_btn)
    
    def setup_connections(self):
        """Setup signal connections."""
        # Table of contents navigation
        self.toc.section_selected.connect(self.content_browser.load_section)
        
        # Helper action handling
        self.content_browser.helper_action_triggered.connect(self.handle_helper_action)
    
    def load_initial_section(self):
        """Load the initial help section."""
        # Load quick start by default
        self.content_browser.load_section("quick-start")
        self.toc.select_section("quick-start")
    
    def navigate_to_section(self, index: int):
        """Navigate to section by index (for keyboard shortcuts)."""
        if 0 <= index < len(self.toc.help_sections):
            section_id = self.toc.help_sections[index][0]
            self.content_browser.load_section(section_id)
            self.toc.select_section(section_id)
    
    def open_find_dialog(self):
        """Open find dialog for searching in current page."""
        text, ok = QInputDialog.getText(
            self, 
            "Find in Page", 
            "Search for:",
            text=getattr(self, '_last_search', '')
        )
        
        if ok and text:
            self._last_search = text
            self.content_browser.search_in_content(text)
    
    def handle_helper_action(self, action: str):
        """Handle helper action links."""
        try:
            if action == "copy-data-folder-path":
                self._copy_data_folder_path()
            
            elif action == "open-data-folder":
                self._open_data_folder()
            
            elif action == "reset-formatting":
                self._reset_formatting()
            
            else:
                logger.warning(f"Unknown helper action: {action}")
                QMessageBox.warning(
                    self,
                    "Unknown Action",
                    f"The helper action '{action}' is not recognized."
                )
        
        except Exception as e:
            logger.error(f"Failed to execute helper action {action}: {e}")
            QMessageBox.critical(
                self,
                "Action Failed",
                f"Failed to execute '{action}': {e}"
            )
    
    def _copy_data_folder_path(self):
        """Copy data folder path to clipboard."""
        try:
            data_dir = get_setting("data_directory", Path.home() / "PocketJournal")
            
            clipboard = QApplication.clipboard()
            clipboard.setText(str(data_dir))
            
            # Show confirmation
            QMessageBox.information(
                self,
                "Path Copied",
                f"Data folder path copied to clipboard:\n{data_dir}"
            )
            
            logger.debug(f"Copied data folder path to clipboard: {data_dir}")
            
        except Exception as e:
            logger.error(f"Failed to copy data folder path: {e}")
            QMessageBox.critical(
                self,
                "Copy Failed",
                f"Failed to copy data folder path: {e}"
            )
    
    def _open_data_folder(self):
        """Open data folder in file explorer."""
        try:
            data_dir = get_setting("data_directory", Path.home() / "PocketJournal")
            open_data_folder(data_dir)
            
            logger.debug(f"Opened data folder: {data_dir}")
            
        except Exception as e:
            logger.error(f"Failed to open data folder: {e}")
            QMessageBox.critical(
                self,
                "Open Failed",
                f"Failed to open data folder: {e}"
            )
    
    def _reset_formatting(self):
        """Reset formatting rules to defaults."""
        try:
            reply = QMessageBox.question(
                self,
                "Reset Formatting",
                "This will reset all formatting rules to their default settings. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Reset all formatting rules to default (enabled)
                formatting_rules = [
                    "all_caps", "emphatic_exclamation", "important_phrases",
                    "parentheticals", "note_lines", "action_lines",
                    "bullet_lists", "numbered_lists"
                ]
                
                for rule in formatting_rules:
                    set_setting(f"formatting_rule_{rule}", True)
                
                QMessageBox.information(
                    self,
                    "Reset Complete",
                    "All formatting rules have been reset to defaults."
                )
                
                logger.debug("Reset formatting rules to defaults")
        
        except Exception as e:
            logger.error(f"Failed to reset formatting: {e}")
            QMessageBox.critical(
                self,
                "Reset Failed",
                f"Failed to reset formatting: {e}"
            )
    
    def show_about(self):
        """Show about dialog."""
        from .about_dialog import show_about_dialog
        show_about_dialog(self)
    
    def keyPressEvent(self, event):
        """Handle key press events for navigation."""
        if event.key() == Qt.Key.Key_F1:
            self.close()
        else:
            super().keyPressEvent(event)


def show_help_center(parent=None, section: Optional[str] = None):
    """
    Show the help center dialog.
    
    Args:
        parent: Parent widget for the dialog
        section: Optional section to navigate to
        
    Returns:
        HelpCenter: The help center dialog instance
    """
    help_center = HelpCenter(parent)
    
    if section:
        help_center.content_browser.load_section(section)
        help_center.toc.select_section(section)
    
    help_center.show()
    help_center.raise_()
    help_center.activateWindow()
    
    return help_center


# Import this for QInputDialog
from PySide6.QtWidgets import QInputDialog