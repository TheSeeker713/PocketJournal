"""
File system scanning and change detection for PocketJournal.

This module implements comprehensive file system scanning with include/exclude rules,
change detection, and efficient caching to avoid unnecessary reprocessing.
"""

import fnmatch
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from PIL import Image

from ..data.database import get_database, FileRecord, FilesTable
from ..settings import settings

logger = logging.getLogger(__name__)


class ScanRule:
    """Represents an include or exclude rule for file scanning."""
    
    def __init__(self, pattern: str, rule_type: str = "include", case_sensitive: bool = False):
        """
        Initialize a scan rule.
        
        Args:
            pattern: Glob pattern to match against
            rule_type: "include" or "exclude"
            case_sensitive: Whether the pattern is case sensitive
        """
        self.pattern = pattern
        self.rule_type = rule_type
        self.case_sensitive = case_sensitive
        
        # Pre-compile pattern for efficiency
        if not case_sensitive:
            self.pattern = self.pattern.lower()
    
    def matches(self, path: Path) -> bool:
        """Check if a path matches this rule."""
        test_path = str(path)
        if not self.case_sensitive:
            test_path = test_path.lower()
        
        # Check against full path and just filename
        return (fnmatch.fnmatch(test_path, self.pattern) or 
                fnmatch.fnmatch(path.name if self.case_sensitive else path.name.lower(), self.pattern))


class ScanConfig:
    """Configuration for file system scanning."""
    
    def __init__(self):
        """Initialize scan configuration with defaults."""
        # Basic settings
        self.recursive = True
        self.follow_symlinks = False
        self.max_depth = 10
        self.min_file_size = 1  # bytes
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        
        # Image settings
        self.min_image_size = 256  # pixels (width or height)
        self.check_image_dimensions = True
        
        # Performance settings
        self.batch_size = 1000
        self.max_scan_time = 300  # seconds
        
        # Default include/exclude rules
        self.rules = [
            # Include common document and text files
            ScanRule("*.md", "include"),
            ScanRule("*.txt", "include"), 
            ScanRule("*.journal", "include"),
            ScanRule("*.pdf", "include"),
            ScanRule("*.doc", "include"),
            ScanRule("*.docx", "include"),
            
            # Include common image formats
            ScanRule("*.jpg", "include"),
            ScanRule("*.jpeg", "include"),
            ScanRule("*.png", "include"),
            ScanRule("*.gif", "include"),
            ScanRule("*.bmp", "include"),
            ScanRule("*.webp", "include"),
            
            # Exclude system and cache directories
            ScanRule("*/.git/*", "exclude"),
            ScanRule("*/.svn/*", "exclude"),
            ScanRule("*/node_modules/*", "exclude"),
            ScanRule("*/__pycache__/*", "exclude"),
            ScanRule("*/.pytest_cache/*", "exclude"),
            ScanRule("*/venv/*", "exclude"),
            ScanRule("*/.venv/*", "exclude"),
            ScanRule("*/build/*", "exclude"),
            ScanRule("*/dist/*", "exclude"),
            ScanRule("*.tmp", "exclude"),
            ScanRule("*.temp", "exclude"),
            ScanRule("*~", "exclude"),
            ScanRule("*.bak", "exclude"),
            
            # Exclude Windows system files
            ScanRule("*/System Volume Information/*", "exclude"),
            ScanRule("*/$RECYCLE.BIN/*", "exclude"),
            ScanRule("*/hiberfil.sys", "exclude"),
            ScanRule("*/pagefile.sys", "exclude"),
            ScanRule("*/swapfile.sys", "exclude"),
            ScanRule("desktop.ini", "exclude"),
            ScanRule("thumbs.db", "exclude"),
            ScanRule("*.lnk", "exclude"),
        ]
    
    def add_rule(self, pattern: str, rule_type: str = "include", case_sensitive: bool = False):
        """Add a new scanning rule."""
        self.rules.append(ScanRule(pattern, rule_type, case_sensitive))
    
    def should_include_path(self, path: Path) -> bool:
        """
        Determine if a path should be included based on rules.
        
        Rules are evaluated in order. The last matching rule determines the result.
        If no rules match, the default is to include the file.
        """
        last_match = "include"  # Default
        
        for rule in self.rules:
            if rule.matches(path):
                last_match = rule.rule_type
        
        return last_match == "include"
    
    @classmethod
    def from_settings(cls) -> 'ScanConfig':
        """Create scan config from application settings."""
        config = cls()
        
        # Load settings
        config.recursive = settings.get("scan.recursive", True)
        config.follow_symlinks = settings.get("scan.follow_symlinks", False)
        config.max_depth = settings.get("scan.max_depth", 10)
        config.min_file_size = settings.get("scan.min_file_size", 1)
        config.max_file_size = settings.get("scan.max_file_size", 100 * 1024 * 1024)
        config.min_image_size = settings.get("scan.min_image_size", 256)
        config.check_image_dimensions = settings.get("scan.check_image_dimensions", True)
        config.batch_size = settings.get("scan.batch_size", 1000)
        config.max_scan_time = settings.get("scan.max_scan_time", 300)
        
        # Load custom rules if any
        custom_rules = settings.get("scan.custom_rules", [])
        for rule_data in custom_rules:
            if isinstance(rule_data, dict):
                config.add_rule(
                    rule_data.get("pattern", ""),
                    rule_data.get("type", "include"),
                    rule_data.get("case_sensitive", False)
                )
        
        return config


class ScanResult:
    """Results from a file system scan."""
    
    def __init__(self):
        """Initialize scan result."""
        self.start_time = datetime.now()
        self.end_time = None
        self.scanned_paths: List[Path] = []
        self.files_found = 0
        self.files_processed = 0
        self.files_skipped = 0
        self.files_unchanged = 0
        self.files_updated = 0
        self.files_new = 0
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # File type statistics
        self.files_by_type: Dict[str, int] = {}
        
        # Size statistics
        self.total_size_bytes = 0
        self.largest_file_size = 0
        self.smallest_file_size = float('inf')
    
    def add_file(self, file_record: FileRecord, was_updated: bool):
        """Add a file to the scan results."""
        self.files_found += 1
        self.files_processed += 1
        
        if was_updated:
            self.files_updated += 1
        else:
            self.files_new += 1
        
        # Update type statistics
        file_type = file_record.file_type
        self.files_by_type[file_type] = self.files_by_type.get(file_type, 0) + 1
        
        # Update size statistics
        size = file_record.size_bytes
        self.total_size_bytes += size
        self.largest_file_size = max(self.largest_file_size, size)
        if size > 0:
            self.smallest_file_size = min(self.smallest_file_size, size)
    
    def add_error(self, error: str):
        """Add an error to the scan results."""
        self.errors.append(error)
        logger.error(f"Scan error: {error}")
    
    def add_warning(self, warning: str):
        """Add a warning to the scan results."""
        self.warnings.append(warning)
        logger.warning(f"Scan warning: {warning}")
    
    def finalize(self):
        """Finalize the scan results."""
        self.end_time = datetime.now()
        if self.smallest_file_size == float('inf'):
            self.smallest_file_size = 0
    
    @property
    def duration_seconds(self) -> float:
        """Get scan duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of scan results."""
        return {
            'duration_seconds': round(self.duration_seconds, 2),
            'files_found': self.files_found,
            'files_processed': self.files_processed,
            'files_new': self.files_new,
            'files_updated': self.files_updated,
            'files_unchanged': self.files_unchanged,
            'files_skipped': self.files_skipped,
            'total_size_mb': round(self.total_size_bytes / (1024 * 1024), 2),
            'files_by_type': self.files_by_type,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }


class FileSystemScanner:
    """
    Comprehensive file system scanner with change detection.
    """
    
    def __init__(self, config: Optional[ScanConfig] = None):
        """Initialize the scanner."""
        self.config = config or ScanConfig.from_settings()
        self.db = get_database()
        self.files_table = FilesTable(self.db.files_table)
        
    def _check_image_dimensions(self, file_path: Path) -> bool:
        """
        Check if an image meets minimum dimension requirements.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            True if image meets requirements, False otherwise
        """
        if not self.config.check_image_dimensions:
            return True
        
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                return (width >= self.config.min_image_size or 
                       height >= self.config.min_image_size)
        except Exception as e:
            logger.warning(f"Could not check image dimensions for {file_path}: {e}")
            return True  # Include if we can't check
    
    def _should_process_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Determine if a file should be processed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (should_process, reason)
        """
        try:
            # Check if file exists and is readable
            if not file_path.exists():
                return False, "File does not exist"
            
            if not file_path.is_file():
                return False, "Not a regular file"
            
            # Check include/exclude rules
            if not self.config.should_include_path(file_path):
                return False, "Excluded by rules"
            
            # Check file size
            try:
                size = file_path.stat().st_size
                if size < self.config.min_file_size:
                    return False, f"File too small ({size} bytes)"
                if size > self.config.max_file_size:
                    return False, f"File too large ({size} bytes)"
            except OSError as e:
                return False, f"Cannot stat file: {e}"
            
            # Check image dimensions if it's an image
            suffix = file_path.suffix.lower()
            if suffix in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                if not self._check_image_dimensions(file_path):
                    return False, f"Image too small (< {self.config.min_image_size}px)"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Error checking file: {e}"
    
    def _has_file_changed(self, file_path: Path, existing_record: FileRecord) -> bool:
        """
        Check if a file has changed since last scan.
        
        Args:
            file_path: Path to the file
            existing_record: Existing database record
            
        Returns:
            True if file has changed, False otherwise
        """
        try:
            stat = file_path.stat()
            
            # Check size and modification time
            return (stat.st_size != existing_record.size_bytes or 
                   abs(stat.st_mtime - existing_record.mtime) > 1.0)  # 1 second tolerance
            
        except OSError:
            # If we can't stat the file, assume it changed
            return True
    
    def _scan_directory(self, directory: Path, result: ScanResult, depth: int = 0) -> Set[str]:
        """
        Scan a single directory.
        
        Args:
            directory: Directory to scan
            result: Scan result to update
            depth: Current recursion depth
            
        Returns:
            Set of path hashes for found files
        """
        found_hashes = set()
        
        try:
            if not directory.exists() or not directory.is_dir():
                result.add_warning(f"Directory does not exist or is not a directory: {directory}")
                return found_hashes
            
            # Check depth limit
            if depth > self.config.max_depth:
                result.add_warning(f"Maximum depth exceeded for {directory}")
                return found_hashes
            
            # Scan directory contents
            try:
                entries = list(directory.iterdir())
            except PermissionError:
                result.add_warning(f"Permission denied accessing directory: {directory}")
                return found_hashes
            
            for entry in entries:
                # Check scan time limit
                if result.duration_seconds > self.config.max_scan_time:
                    result.add_warning("Scan time limit exceeded")
                    break
                
                try:
                    if entry.is_file():
                        self._process_file(entry, result, found_hashes)
                    elif entry.is_dir() and self.config.recursive:
                        # Recursively scan subdirectory
                        if self.config.follow_symlinks or not entry.is_symlink():
                            subdir_hashes = self._scan_directory(entry, result, depth + 1)
                            found_hashes.update(subdir_hashes)
                
                except PermissionError:
                    result.add_warning(f"Permission denied accessing: {entry}")
                except Exception as e:
                    result.add_error(f"Error processing {entry}: {e}")
        
        except Exception as e:
            result.add_error(f"Error scanning directory {directory}: {e}")
        
        return found_hashes
    
    def _process_file(self, file_path: Path, result: ScanResult, found_hashes: Set[str]):
        """
        Process a single file.
        
        Args:
            file_path: Path to the file
            result: Scan result to update
            found_hashes: Set to add path hash to
        """
        try:
            # Check if file should be processed
            should_process, reason = self._should_process_file(file_path)
            if not should_process:
                result.files_skipped += 1
                logger.debug(f"Skipping {file_path}: {reason}")
                return
            
            # Create file record
            scan_time = datetime.now()
            file_record = FileRecord.from_file_path(file_path, scan_time)
            path_hash = file_record.path_hash
            found_hashes.add(path_hash)
            
            # Check if file exists in database
            existing_record = self.files_table.get_by_path_hash(path_hash)
            
            if existing_record:
                # File exists, check if it changed
                if self._has_file_changed(file_path, existing_record):
                    # File changed, update record
                    file_record.data['scan_count'] = existing_record.data.get('scan_count', 0) + 1
                    file_record.data['is_processed'] = False  # Mark for reprocessing
                    was_updated = self.files_table.upsert_file(file_record)
                    result.add_file(file_record, was_updated)
                    logger.debug(f"Updated changed file: {file_path}")
                else:
                    # File unchanged, just update last_seen_at
                    self.files_table.update_last_seen(path_hash, scan_time)
                    result.files_unchanged += 1
                    logger.debug(f"File unchanged: {file_path}")
            else:
                # New file, insert record
                was_updated = self.files_table.upsert_file(file_record)
                result.add_file(file_record, was_updated)
                logger.debug(f"Added new file: {file_path}")
                
        except Exception as e:
            result.add_error(f"Error processing file {file_path}: {e}")
    
    def scan_paths(self, paths: List[Union[str, Path]]) -> ScanResult:
        """
        Scan multiple paths.
        
        Args:
            paths: List of paths to scan
            
        Returns:
            ScanResult with scan statistics
        """
        result = ScanResult()
        result.scanned_paths = [Path(p) for p in paths]
        
        logger.info(f"Starting scan of {len(paths)} paths")
        
        all_found_hashes = set()
        
        try:
            for path in result.scanned_paths:
                path_obj = Path(path)
                
                if path_obj.is_file():
                    # Scan single file
                    self._process_file(path_obj, result, all_found_hashes)
                elif path_obj.is_dir():
                    # Scan directory
                    found_hashes = self._scan_directory(path_obj, result)
                    all_found_hashes.update(found_hashes)
                else:
                    result.add_warning(f"Path does not exist or is not accessible: {path}")
            
            # Clean up database (remove records for files that no longer exist)
            # Note: Only do this if we scanned directories, not individual files
            dir_scans = [p for p in result.scanned_paths if Path(p).is_dir()]
            if dir_scans and settings.get("scan.cleanup_missing_files", True):
                cleanup_count = self.files_table.cleanup_missing_files(list(all_found_hashes))
                if cleanup_count > 0:
                    logger.info(f"Cleaned up {cleanup_count} missing file records")
                    result.add_warning(f"Removed {cleanup_count} records for missing files")
            
        except Exception as e:
            result.add_error(f"Critical scan error: {e}")
        
        finally:
            result.finalize()
        
        logger.info(f"Scan completed in {result.duration_seconds:.2f}s: "
                   f"{result.files_found} found, {result.files_new} new, "
                   f"{result.files_updated} updated, {result.files_unchanged} unchanged")
        
        return result
    
    def scan_path(self, path: Union[str, Path]) -> ScanResult:
        """
        Scan a single path.
        
        Args:
            path: Path to scan
            
        Returns:
            ScanResult with scan statistics
        """
        return self.scan_paths([path])


def scan_directories(directories: List[Union[str, Path]], 
                    config: Optional[ScanConfig] = None) -> ScanResult:
    """
    Convenience function to scan directories.
    
    Args:
        directories: List of directories to scan
        config: Optional scan configuration
        
    Returns:
        ScanResult with scan statistics
    """
    scanner = FileSystemScanner(config)
    return scanner.scan_paths(directories)