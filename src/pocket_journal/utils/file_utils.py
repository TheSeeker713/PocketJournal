"""
File utilities for PocketJournal.
Provides file system operations and path management.
"""

import os
import re
from pathlib import Path
from typing import Union


def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """Ensure directory exists, creating it if necessary."""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces and other characters with hyphens
    filename = re.sub(r'[\s\-_]+', '-', filename)
    
    # Remove leading/trailing hyphens and dots
    filename = filename.strip('-._')
    
    # Ensure not empty
    if not filename:
        filename = "untitled"
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename


def get_safe_filename(base_name: str, directory: Path, extension: str = "") -> str:
    """Get safe filename that doesn't conflict with existing files."""
    base_name = sanitize_filename(base_name)
    
    if extension and not extension.startswith('.'):
        extension = f".{extension}"
    
    filename = f"{base_name}{extension}"
    file_path = directory / filename
    
    # If file doesn't exist, return the name
    if not file_path.exists():
        return filename
    
    # Generate unique name with counter
    counter = 1
    while True:
        filename = f"{base_name}_{counter}{extension}"
        file_path = directory / filename
        if not file_path.exists():
            return filename
        counter += 1


def get_file_size_human(file_path: Union[str, Path]) -> str:
    """Get human-readable file size."""
    try:
        size = Path(file_path).stat().st_size
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} TB"
    except (OSError, FileNotFoundError):
        return "Unknown"


def normalize_path(path: Union[str, Path]) -> Path:
    """Normalize path for consistent handling."""
    return Path(path).resolve()


def is_text_file(file_path: Union[str, Path]) -> bool:
    """Check if file is likely a text file."""
    try:
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml'}
        return Path(file_path).suffix.lower() in text_extensions
    except Exception:
        return False


def backup_file(file_path: Union[str, Path], backup_suffix: str = ".bak") -> bool:
    """Create backup of file."""
    try:
        source_path = Path(file_path)
        if not source_path.exists():
            return False
        
        backup_path = source_path.with_suffix(source_path.suffix + backup_suffix)
        
        # Read and write to ensure proper copying
        content = source_path.read_bytes()
        backup_path.write_bytes(content)
        
        return backup_path.exists()
    except Exception as e:
        print(f"Error creating backup of {file_path}: {e}")
        return False