"""
Entry management system for PocketJournal.
Handles entry lifecycle, autosave, timestamps, and file operations.
"""

import os
import re
import uuid
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from ..settings import get_setting
from ..utils.file_utils import ensure_directory_exists, sanitize_filename


@dataclass
class EntryMetadata:
    """Entry metadata structure for YAML front-matter."""
    id: str
    created_at: str  # ISO UTC timestamp
    updated_at: str  # ISO UTC timestamp
    title: str
    subtitle: str
    tags: List[str]
    word_count: int
    path: str


class Entry:
    """Represents a journal entry with metadata and content."""
    
    def __init__(self, content: str = "", metadata: Optional[EntryMetadata] = None):
        """Initialize entry with content and optional metadata."""
        self.content = content
        self.metadata = metadata or self._create_default_metadata()
        self._original_content = content
        self._is_new = metadata is None
    
    def _create_default_metadata(self) -> EntryMetadata:
        """Create default metadata for new entry."""
        now_utc = datetime.now(timezone.utc).isoformat()
        entry_id = str(uuid.uuid4())
        
        return EntryMetadata(
            id=entry_id,
            created_at=now_utc,
            updated_at=now_utc,
            title="",
            subtitle="",
            tags=[],
            word_count=0,
            path=""
        )
    
    @property
    def is_new(self) -> bool:
        """Check if this is a new entry."""
        return self._is_new
    
    @property
    def is_modified(self) -> bool:
        """Check if entry content has been modified."""
        return self.content != self._original_content
    
    def update_metadata(self):
        """Update metadata based on current content."""
        # Update timestamp
        self.metadata.updated_at = datetime.now(timezone.utc).isoformat()
        
        # Update word count
        self.metadata.word_count = len(self.content.split()) if self.content.strip() else 0
        
        # Extract title from first line if not set or if content changed
        if not self.metadata.title and self.content.strip():
            first_line = self.content.split('\n')[0].strip()
            # Remove markdown heading markers
            title = re.sub(r'^#+\s*', '', first_line)
            self.metadata.title = title[:100] if title else ""
        elif self.content.strip():
            # If title is already set but content starts with a heading, use that
            first_line = self.content.split('\n')[0].strip()
            if first_line.startswith('#'):
                title = re.sub(r'^#+\s*', '', first_line)
                self.metadata.title = title[:100] if title else self.metadata.title
    
    def generate_filename(self) -> str:
        """Generate filename based on metadata."""
        # Use creation time for filename
        created_dt = datetime.fromisoformat(self.metadata.created_at.replace('Z', '+00:00'))
        
        # Format: YYYY-MM-DD_HH-MM-SS_slug.md
        timestamp_part = created_dt.strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create slug from title
        if self.metadata.title:
            slug = sanitize_filename(self.metadata.title[:50])
            slug = re.sub(r'[^\w\-_]', '', slug)
            slug = re.sub(r'[-_]+', '-', slug).strip('-_')
            if not slug:
                slug = self.metadata.id[:8]
        else:
            slug = self.metadata.id[:8]
        
        return f"{timestamp_part}_{slug}.md"
    
    def to_markdown(self) -> str:
        """Convert entry to markdown with YAML front-matter."""
        # Update metadata before serializing
        self.update_metadata()
        
        # Create YAML front-matter
        yaml_data = asdict(self.metadata)
        yaml_content = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
        
        # Combine front-matter and content
        return f"---\n{yaml_content}---\n\n{self.content}"
    
    @classmethod
    def from_markdown(cls, markdown_content: str, file_path: str = "") -> 'Entry':
        """Create entry from markdown with YAML front-matter."""
        # Split front-matter and content
        if markdown_content.startswith('---\n'):
            try:
                parts = markdown_content.split('---\n', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    content = parts[2].strip()
                    
                    # Parse YAML metadata
                    yaml_data = yaml.safe_load(yaml_content)
                    metadata = EntryMetadata(**yaml_data)
                    metadata.path = file_path
                    
                    entry = cls(content, metadata)
                    entry._original_content = content
                    entry._is_new = False
                    return entry
            except (yaml.YAMLError, TypeError) as e:
                print(f"Error parsing YAML front-matter: {e}")
        
        # Fallback: treat as plain content
        entry = cls(markdown_content.strip())
        if file_path:
            entry.metadata.path = file_path
        return entry


class EntryManager:
    """Manages entry persistence and file operations."""
    
    def __init__(self):
        """Initialize entry manager."""
        self.base_path = self._get_base_path()
        self.current_entry: Optional[Entry] = None
        self._last_save_time: Optional[datetime] = None
    
    def _get_base_path(self) -> Path:
        """Get base path for storing entries."""
        # Default to Documents\PocketJournal\Entries
        documents_path = Path.home() / "Documents"
        base_path = documents_path / "PocketJournal" / "Entries"
        
        # Allow override from settings
        custom_path = get_setting("entries_path", "")
        if custom_path:
            base_path = Path(custom_path)
        
        ensure_directory_exists(base_path)
        return base_path
    
    def _get_entry_directory(self, created_at: str) -> Path:
        """Get directory for entry based on creation date."""
        # Parse ISO timestamp
        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        # Create YYYY/MM directory structure
        year = created_dt.strftime("%Y")
        month = created_dt.strftime("%m")
        
        entry_dir = self.base_path / year / month
        ensure_directory_exists(entry_dir)
        return entry_dir
    
    def create_new_entry(self, initial_content: str = "") -> Entry:
        """Create a new entry with default metadata."""
        entry = Entry(initial_content)
        self.current_entry = entry
        return entry
    
    def load_entry(self, file_path: str) -> Optional[Entry]:
        """Load entry from file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            content = path.read_text(encoding='utf-8')
            entry = Entry.from_markdown(content, str(path))
            self.current_entry = entry
            return entry
            
        except Exception as e:
            print(f"Error loading entry from {file_path}: {e}")
            return None
    
    def save_entry(self, entry: Entry, force: bool = False) -> bool:
        """Save entry to file system."""
        try:
            # Skip save if no changes (unless forced)
            if not force and not entry.is_modified and not entry.is_new:
                return True
            
            # Update metadata
            entry.update_metadata()
            
            # Get target directory
            entry_dir = self._get_entry_directory(entry.metadata.created_at)
            
            # Generate filename if not set
            if not entry.metadata.path:
                filename = entry.generate_filename()
                file_path = entry_dir / filename
                entry.metadata.path = str(file_path)
            else:
                file_path = Path(entry.metadata.path)
            
            # Ensure target directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            markdown_content = entry.to_markdown()
            file_path.write_text(markdown_content, encoding='utf-8')
            
            # Update tracking
            entry._original_content = entry.content
            entry._is_new = False
            self._last_save_time = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error saving entry: {e}")
            return False
    
    def get_recent_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of recent entries (metadata only)."""
        entries = []
        
        try:
            # Walk through year/month directories
            for year_dir in sorted(self.base_path.glob("*"), reverse=True):
                if not year_dir.is_dir():
                    continue
                    
                for month_dir in sorted(year_dir.glob("*"), reverse=True):
                    if not month_dir.is_dir():
                        continue
                    
                    # Get markdown files
                    md_files = sorted(month_dir.glob("*.md"), reverse=True)
                    
                    for md_file in md_files:
                        if len(entries) >= limit:
                            return entries
                        
                        try:
                            # Read just the front-matter for metadata
                            content = md_file.read_text(encoding='utf-8')
                            if content.startswith('---\n'):
                                parts = content.split('---\n', 2)
                                if len(parts) >= 2:
                                    yaml_content = parts[1]
                                    metadata = yaml.safe_load(yaml_content)
                                    metadata['file_path'] = str(md_file)
                                    entries.append(metadata)
                        except Exception as e:
                            print(f"Error reading entry metadata from {md_file}: {e}")
                            continue
            
        except Exception as e:
            print(f"Error getting recent entries: {e}")
        
        return entries
    
    def search_entries(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search entries by content and metadata."""
        results = []
        query_lower = query.lower()
        
        try:
            # Walk through all entry files
            for md_file in self.base_path.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    entry = Entry.from_markdown(content, str(md_file))
                    
                    # Search in title, content, and tags
                    searchable_text = (
                        f"{entry.metadata.title} {entry.content} {' '.join(entry.metadata.tags)}"
                    ).lower()
                    
                    if query_lower in searchable_text:
                        result = asdict(entry.metadata)
                        result['file_path'] = str(md_file)
                        # Add snippet of matching content
                        content_lower = entry.content.lower()
                        if query_lower in content_lower:
                            idx = content_lower.find(query_lower)
                            start = max(0, idx - 50)
                            end = min(len(entry.content), idx + 100)
                            result['snippet'] = entry.content[start:end]
                        results.append(result)
                        
                        if len(results) >= limit:
                            break
                            
                except Exception as e:
                    print(f"Error searching entry {md_file}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error during search: {e}")
        
        return results
    
    @property
    def last_save_time(self) -> Optional[datetime]:
        """Get timestamp of last save operation."""
        return self._last_save_time
    
    def cleanup_empty_entries(self):
        """Remove entries with no content."""
        try:
            for md_file in self.base_path.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding='utf-8').strip()
                    entry = Entry.from_markdown(content, str(md_file))
                    
                    # Remove if no meaningful content
                    if not entry.content.strip() and entry.metadata.word_count == 0:
                        md_file.unlink()
                        print(f"Removed empty entry: {md_file}")
                        
                except Exception as e:
                    print(f"Error checking entry {md_file}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error during cleanup: {e}")