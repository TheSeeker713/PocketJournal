# Privacy & Data Security

PocketJournal is designed with privacy and data security as core principles. Your notes are yours, stored locally, and never transmitted elsewhere.

## Data Storage Philosophy

### Local-Only Storage
- **All data stays on your device**
- No cloud synchronization or remote storage
- No account creation or sign-up required
- No tracking or analytics

### Standard File Formats
- Plain text Markdown files
- Standard YAML metadata
- No proprietary or encrypted formats
- Full user control and ownership

## What Data Is Stored

### Entry Content
**Your Notes**
- Text content you write
- Automatically extracted titles and subtitles
- Creation and modification timestamps
- Word and character counts

**File Metadata**
- Standard file system timestamps
- File sizes and permissions
- Directory organization by date

### Application Settings
**Preferences**
- UI customization (theme, fonts, sizes)
- Formatting rule preferences
- Export settings and locations
- Window positions and sizes

**System Integration**
- Global hotkey registration
- Startup preferences (Windows registry)
- File association preferences

### What Is NOT Stored
- Personal identifying information
- Usage analytics or telemetry
- Crash reports or error logs (unless explicitly saved)
- Network activity or external communications

## Data Location

### Default Storage
```
Windows: %USERPROFILE%\Documents\PocketJournal\
macOS:   ~/Documents/PocketJournal/
Linux:   ~/Documents/PocketJournal/
```

### User-Configurable
- Data directory can be changed in Settings
- Supports any writable location
- Network drives and external storage supported
- Portable installation possible

### File Structure
```
PocketJournal/
├── Entries/          # Your note files
│   ├── YYYY/MM/      # Organized by date
│   └── *.md          # Markdown files
├── Exports/          # Exported files
├── Backups/          # Deleted file backups
└── .settings/        # Application preferences
```

## Security Measures

### File System Security
**Standard Permissions**
- Files created with user-only permissions
- Respects system file access controls
- No elevated privileges required

**Backup Protection**
- Automatic backup files (.bak) available
- Deleted files moved to Backups/ folder
- 10-second undo window for deletions

### No Network Activity
**Offline Operation**
- No internet connection required
- No data transmission to servers
- No update checks or phone-home behavior

**Local Processing**
- All search and indexing performed locally
- No cloud-based AI or processing
- Your data never leaves your device

## Data Control

### Full Data Ownership
**Direct File Access**
- All files are standard formats
- Can be opened in any text editor
- No vendor lock-in or proprietary formats
- Easy to backup and migrate

**Export Options**
- Multiple export formats available
- Batch export capabilities
- Preserve or strip metadata as desired
- Full control over exported data

### Data Portability
**Platform Independence**
- Files work on any operating system
- No special software required to read
- Standard Markdown format ensures longevity
- Easy migration between devices

**Import/Export Freedom**
- Export to any format or location
- Import from other applications
- No restrictions on data movement
- Standard file operations supported

## Deletion and Cleanup

### Secure Deletion
**File Removal**
- Deleted files moved to Backups/ folder
- Can be permanently deleted manually
- Standard file system deletion applies
- No special secure deletion (use system tools if needed)

**Data Cleanup**
- Empty entry cleanup available
- Backup file management
- Settings reset functionality
- Complete uninstall removes all traces

### Retention Policy
**User Controlled**
- No automatic data deletion
- All retention decisions made by user
- Backup files persist until manually removed
- Full control over data lifecycle

## Third-Party Components

### Open Source Foundation
**Qt/PySide6 Framework**
- Well-established UI framework
- Open source with transparent security practices
- No data collection by framework

**Python Runtime**
- Standard Python interpreter
- No additional network libraries
- Minimal external dependencies

### No Analytics or Tracking
- No Google Analytics or similar services
- No crash reporting services
- No usage metrics collection
- No advertising or marketing integrations

## Compliance and Standards

### Data Protection
**GDPR Compliance**
- No personal data processing
- No data sharing with third parties
- User maintains full data control
- Right to deletion inherently supported

**Local Data Laws**
- Complies with local storage regulations
- No cross-border data transfer
- User responsible for their own data handling

### Industry Standards
**Best Practices**
- Minimal data collection principle
- Transparent data handling
- User control and consent
- Security by design

## Recommendations

### Protecting Your Data
**Regular Backups**
- Enable automatic backup files in Settings
- Regularly backup PocketJournal folder
- Consider cloud backup of entire folder (your choice)
- Test restore procedures periodically

**Access Control**
- Use system user accounts appropriately
- Consider disk encryption for sensitive notes
- Secure your device with appropriate authentication
- Be mindful of shared computers

### Sharing Considerations
**When Sharing Notes**
- Review metadata before sharing exports
- Consider stripping timestamps if sensitive
- Use plain text export for maximum privacy
- Be aware of content in shared files

**Collaborative Work**
- PocketJournal is designed for personal use
- For collaboration, use explicit export/sharing
- Consider dedicated collaboration tools for teams
- Maintain awareness of shared content

## Frequently Asked Questions

**Q: Does PocketJournal send any data over the internet?**
A: No. PocketJournal operates entirely offline and never transmits data.

**Q: Can other applications access my PocketJournal data?**
A: Only if they have file system access to your data directory. Standard file permissions apply.

**Q: What happens if I uninstall PocketJournal?**
A: Your data files remain in the Documents/PocketJournal folder. You can delete them manually if desired.

**Q: Can I password-protect my entries?**
A: PocketJournal doesn't provide built-in encryption. Use system-level disk encryption or third-party file encryption tools.

**Q: Is it safe to store PocketJournal data in cloud storage?**
A: That's your choice. The files are standard Markdown, so any backup or sync solution you trust can be used.

**Q: Does PocketJournal log my activity?**
A: Only minimal application logs for debugging (if enabled). No activity tracking or usage analytics.

## Contact and Transparency

### Open Source
- PocketJournal source code is available for review
- Security practices are transparent
- Community contributions welcome
- No hidden functionality

### Support
- Support requests don't require personal information
- No account or registration needed
- Privacy-respecting communication channels

**Next:** View the complete [Keyboard Shortcuts](shortcuts.md) reference.