"""
About dialog for PocketJournal.

Displays application information, version details, data locations,
and recent changelog entries.
"""

import os
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices

from ..app_meta import APP_NAME, ORG_NAME, VERSION, BUILD_DATE, CHANNEL, get_version_string

logger = logging.getLogger(__name__)


class AboutDialog(QDialog):
    """About dialog showing app info, version, and data locations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setFixedSize(420, 380)
        self.setModal(True)
        
        # Position dialog near left edge of screen
        self.move(50, 100)
        
        # Load changelog content
        self.changelog_entries = self._load_changelog()
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Set modern dark gradient background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:0.5 #34495e, stop:1 #2c3e50);
                color: white;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Header section
        header_widget = self.create_header_section()
        layout.addWidget(header_widget)
        
        # Version and build info
        version_widget = self.create_version_section()
        layout.addWidget(version_widget)
        
        # Data locations section
        data_widget = self.create_data_locations_section()
        layout.addWidget(data_widget)
        
        # Changelog section
        changelog_widget = self.create_changelog_section()
        layout.addWidget(changelog_widget)
        
        # Buttons
        buttons_widget = self.create_buttons_section()
        layout.addWidget(buttons_widget)
    
    def create_header_section(self):
        """Create the header with app name and logo."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(52, 152, 219, 0.8), stop:1 rgba(41, 128, 185, 0.9));
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin: 2px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setSpacing(15)
        
        # App icon with smaller size
        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 30px;
                color: white;
                font-size: 22px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setText("PJ")
        layout.addWidget(icon_label)
        
        # App info with modern typography
        info_layout = QVBoxLayout()
        
        # App name
        name_label = QLabel(APP_NAME)
        name_font = QFont('Segoe UI', 18, QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                border: none;
                margin-bottom: 3px;
            }
        """)
        info_layout.addWidget(name_label)
        
        # Tagline
        tagline_label = QLabel("A Windows-first personal journaling application")
        tagline_font = QFont('Segoe UI', 10)
        tagline_label.setFont(tagline_font)
        tagline_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                background: transparent;
                border: none;
                margin-bottom: 5px;
            }
        """)
        info_layout.addWidget(tagline_label)
        
        # Organization
        org_label = QLabel(f"© 2025 {ORG_NAME}")
        org_font = QFont('Segoe UI', 9)
        org_label.setFont(org_font)
        org_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                background: transparent;
                border: none;
            }
        """)
        info_layout.addWidget(org_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return frame
    
    def create_version_section(self):
        """Create version and build information section."""
        group = QGroupBox("Version Information")
        group.setStyleSheet("""
            QGroupBox {
                background: rgba(44, 62, 80, 0.6);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
                margin-top: 5px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 6px 0 6px;
                color: rgba(255, 255, 255, 0.9);
            }
        """)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 4, 6, 6)
        
        # Version details with compact styling
        version_text = f"""
<table cellpadding="4" cellspacing="0" style="width: 100%; color: rgba(255, 255, 255, 0.9);">
<tr><td style="font-weight: bold; color: #3498db; font-size: 11px;">Version:</td><td style="font-size: 11px;">{VERSION}</td></tr>
<tr><td style="font-weight: bold; color: #3498db; font-size: 11px;">Build Date:</td><td style="font-size: 11px;">{BUILD_DATE}</td></tr>
<tr><td style="font-weight: bold; color: #3498db; font-size: 11px;">Channel:</td><td style="font-size: 11px;">{CHANNEL.title()}</td></tr>
<tr><td style="font-weight: bold; color: #3498db; font-size: 11px;">Full Version:</td><td style="font-size: 11px;">{get_version_string()}</td></tr>
</table>
        """.strip()
        
        version_label = QLabel(version_text)
        version_label.setWordWrap(True)
        version_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: white;
                font-size: 11px;
            }
        """)
        layout.addWidget(version_label)
        
        return group
    
    def create_data_locations_section(self):
        """Create data locations section with open buttons."""
        group = QGroupBox("Data Locations")
        group.setStyleSheet("""
            QGroupBox {
                background: rgba(44, 62, 80, 0.6);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
                margin-top: 5px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 6px 0 6px;
                color: rgba(255, 255, 255, 0.9);
            }
        """)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 4, 6, 6)
        
        # Get data directories
        from ..settings import get_setting
        from platformdirs import user_data_dir, user_config_dir
        from ..app_meta import APP_NAME, ORG_NAME
        
        data_dir = user_data_dir(APP_NAME, ORG_NAME)
        config_dir = user_config_dir(APP_NAME, ORG_NAME)
        
        # Data directory
        data_layout = QHBoxLayout()
        data_label = QLabel(f"<b style='color: #3498db; font-size: 11px;'>Data Directory:</b><br><span style='color: rgba(255,255,255,0.8); font-size: 10px;'>{data_dir}</span>")
        data_label.setWordWrap(True)
        data_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: white;
                padding: 3px;
                font-size: 10px;
            }
        """)
        data_layout.addWidget(data_label)
        
        self.open_data_btn = QPushButton("Open")
        self.open_data_btn.setFixedSize(50, 24)
        self.open_data_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: #2980b9;
            }
        """)
        self.open_data_btn.setToolTip("Open data directory in file explorer")
        data_layout.addWidget(self.open_data_btn)
        layout.addLayout(data_layout)
        
        # Config directory
        config_layout = QHBoxLayout()
        config_label = QLabel(f"<b style='color: #3498db; font-size: 11px;'>Config Directory:</b><br><span style='color: rgba(255,255,255,0.8); font-size: 10px;'>{config_dir}</span>")
        config_label.setWordWrap(True)
        config_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: white;
                padding: 3px;
                font-size: 10px;
            }
        """)
        config_layout.addWidget(config_label)
        
        self.open_config_btn = QPushButton("Open")
        self.open_config_btn.setFixedSize(50, 24)
        self.open_config_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: #2980b9;
            }
        """)
        self.open_config_btn.setToolTip("Open config directory in file explorer")
        config_layout.addWidget(self.open_config_btn)
        layout.addLayout(config_layout)
        
        return group
    
    def create_changelog_section(self):
        """Create changelog section showing recent entries."""
        group = QGroupBox("Recent Changes")
        group.setStyleSheet("""
            QGroupBox {
                background: rgba(44, 62, 80, 0.6);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
                margin-top: 5px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 6px 0 6px;
                color: rgba(255, 255, 255, 0.9);
            }
        """)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 4, 6, 6)
        
        # Changelog text area
        self.changelog_text = QTextEdit()
        self.changelog_text.setMaximumHeight(50)
        self.changelog_text.setReadOnly(True)
        self.changelog_text.setStyleSheet("""
            QTextEdit {
                background: rgba(52, 73, 94, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10px;
                padding: 6px;
                selection-background-color: #3498db;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 3px;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                min-height: 15px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        """)
        
        # Load and display changelog
        changelog_html = self._format_changelog_html()
        self.changelog_text.setHtml(changelog_html)
        
        layout.addWidget(self.changelog_text)
        
        return group
    
    def create_buttons_section(self):
        """Create the bottom buttons section."""
        frame = QFrame()
        frame.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Credits button
        self.credits_btn = QPushButton("Credits")
        self.credits_btn.setFixedSize(80, 30)
        self.credits_btn.setStyleSheet("""
            QPushButton {
                background: rgba(149, 165, 166, 0.8);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(149, 165, 166, 1.0);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background: rgba(127, 140, 141, 1.0);
            }
        """)
        self.credits_btn.setToolTip("Show credits and acknowledgments")
        layout.addWidget(self.credits_btn)
        
        layout.addStretch()
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setDefault(True)
        self.close_btn.setFixedSize(80, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ec7063, stop:1 #e74c3c);
            }
            QPushButton:pressed {
                background: #c0392b;
            }
        """)
        layout.addWidget(self.close_btn)
        
        return frame
    
    def setup_connections(self):
        """Setup signal connections."""
        self.open_data_btn.clicked.connect(self.open_data_directory)
        self.open_config_btn.clicked.connect(self.open_config_directory)
        self.credits_btn.clicked.connect(self.show_credits)
        self.close_btn.clicked.connect(self.accept)
    
    def _load_changelog(self):
        """Load changelog entries from about/changelog.md."""
        changelog_file = Path(__file__).parent.parent.parent.parent / "about" / "changelog.md"
        
        if not changelog_file.exists():
            return []
        
        try:
            with open(changelog_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse changelog entries (simple parsing)
            entries = []
            current_version = None
            current_content = []
            
            for line in content.split('\n'):
                line = line.strip()
                
                # Version header
                if line.startswith('## Version'):
                    if current_version and current_content:
                        entries.append({
                            'version': current_version,
                            'content': '\n'.join(current_content)
                        })
                    
                    current_version = line.replace('## Version ', '').strip()
                    current_content = []
                
                elif current_version and line:
                    current_content.append(line)
            
            # Add last entry
            if current_version and current_content:
                entries.append({
                    'version': current_version,
                    'content': '\n'.join(current_content)
                })
            
            return entries[:3]  # Return latest 3 entries
            
        except Exception as e:
            logger.warning(f"Failed to load changelog: {e}")
            return []
    
    def _format_changelog_html(self):
        """Format changelog entries as HTML."""
        if not self.changelog_entries:
            return "<p><i>No recent changes available.</i></p>"
        
        html_parts = []
        
        for entry in self.changelog_entries:
            version = entry['version']
            content = entry['content']
            
            # Format version header
            html_parts.append(f"<h4 style='color: #4a90e2; margin-bottom: 5px;'>{version}</h4>")
            
            # Format content
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('### '):
                    # Subsection
                    html_parts.append(f"<p style='margin: 3px 0; font-weight: bold;'>{line[4:]}</p>")
                elif line.startswith('- '):
                    # List item
                    html_parts.append(f"<p style='margin: 2px 0 2px 15px; font-size: 9pt;'>• {line[2:]}</p>")
            
            html_parts.append("<br>")
        
        return ''.join(html_parts)
    
    def open_data_directory(self):
        """Open the data directory in file explorer."""
        try:
            from platformdirs import user_data_dir
            from ..app_meta import APP_NAME, ORG_NAME
            
            data_dir = user_data_dir(APP_NAME, ORG_NAME)
            
            # Ensure directory exists
            os.makedirs(data_dir, exist_ok=True)
            
            # Open in file explorer
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(data_dir)))
            
        except Exception as e:
            logger.error(f"Failed to open data directory: {e}")
    
    def open_config_directory(self):
        """Open the config directory in file explorer."""
        try:
            from platformdirs import user_config_dir
            from ..app_meta import APP_NAME, ORG_NAME
            
            config_dir = user_config_dir(APP_NAME, ORG_NAME)
            
            # Ensure directory exists
            os.makedirs(config_dir, exist_ok=True)
            
            # Open in file explorer
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(config_dir)))
            
        except Exception as e:
            logger.error(f"Failed to open config directory: {e}")
    
    def show_credits(self):
        """Show credits and acknowledgments."""
        credits_text = f"""
<h3>Credits & Acknowledgments</h3>

<p><b>{APP_NAME}</b> is built with the following technologies:</p>

<ul>
<li><b>PySide6</b> - Modern Qt bindings for Python</li>
<li><b>Python</b> - The programming language</li>
<li><b>PyYAML</b> - YAML parsing and generation</li>
<li><b>platformdirs</b> - Cross-platform data directories</li>
<li><b>markdown-it-py</b> - Markdown processing</li>
<li><b>pytest</b> - Testing framework</li>
</ul>

<p><b>Special Thanks:</b></p>
<ul>
<li>The Qt Company for the excellent Qt framework</li>
<li>The Python Software Foundation</li>
<li>All open source contributors</li>
</ul>

<p><b>Development:</b><br>
Built with love for personal productivity and journaling.</p>
        """
        
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Credits")
        msg.setText(credits_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()


def show_about_dialog(parent=None):
    """Show the about dialog."""
    dialog = AboutDialog(parent)
    return dialog.exec()