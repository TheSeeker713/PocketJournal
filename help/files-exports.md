# Files & Exports

PocketJournal stores your entries as standard Markdown files and provides flexible export options for sharing and backup.

## File Storage

### Default Location
```
Documents/PocketJournal/Entries/YYYY/MM/
```

### File Format
Each entry is stored as a Markdown file with YAML front-matter:

```markdown
---
title: "Meeting Notes - Project Alpha"
created_at: "2025-10-03T14:30:00.000Z"
updated_at: "2025-10-03T15:45:00.000Z"
word_count: 127
character_count: 742
---

# Meeting Notes - Project Alpha

Discussed the timeline for the new project.

IMPORTANT: Deadline is November 15th

ACTION: Send proposal to client by Friday

Next steps:
- Review requirements
- Create mockups
- Schedule follow-up meeting
```

### Filename Convention
```
YYYY-MM-DD_HH-MM-SS_title-slug.md

Examples:
2025-10-03_14-30-15_meeting-notes-project-alpha.md
2025-10-03_15-45-22_grocery-list.md
2025-10-04_09-00-00_morning-thoughts.md
```

## Data Management

### Accessing Your Files

**Quick Access:**
- Click [Open Data Folder](#open-data-folder) helper link
- Or Settings → Files & Exports → "Open Entries Folder"
- Or Settings → Files & Exports → "Open Data Folder"

**File Explorer Path:**
```
%USERPROFILE%\Documents\PocketJournal\Entries\
```

### Changing Data Location
1. Go to Settings → Files & Exports
2. Click "Change..." next to Data Directory
3. Select new folder location
4. **Note:** Existing entries remain in old location

### Backup Options

**Automatic Backups:**
- Enable in Settings → Files & Exports → "Create backup files"
- Creates `.bak` copies before overwriting
- Helps prevent data loss during saves

**Manual Backup:**
- Copy entire `PocketJournal` folder
- All entries are standard files
- No special export needed

## Export Features

### Single Entry Export
1. Open the entry you want to export
2. Click the **⋯** (more) button
3. Select "Export"
4. Choose format and destination

### Export Formats

**Markdown (.md)**
- Full YAML front-matter preserved
- All formatting and metadata included
- Best for technical users and portability

**Plain Text (.txt)**
- Clean text content only
- No metadata or formatting
- Best for simple sharing and reading

**Rich Text (.rtf)**
- Formatted text with styling
- Preserves bold, italic, underline
- Best for word processors and presentations

### Export Settings

**Configure Defaults:**
Settings → Files & Exports:
- **Default Export Format**: Choose preferred format
- **Export Directory**: Set default export location
- **Include Metadata**: Include/exclude YAML front-matter
- **Preserve Formatting**: Maintain smart formatting in exports

**Export Options:**
- ✅ **Include metadata in exports**: Adds creation date, word count, etc.
- ✅ **Preserve formatting in exports**: Maintains smart formatting
- 📁 **Export Directory**: `Documents/PocketJournal/Exports/` (default)

## File Operations

### Entry Actions Menu (⋯)

**View in Folder**
- Opens file explorer to entry location
- Works on Windows, macOS, and Linux
- Highlights the specific entry file

**Rename Entry**
- Changes the entry filename
- Updates internal references
- Preserves all content and metadata

**Duplicate Entry**
- Creates a copy with new timestamp
- Useful for templates or similar entries
- Copy gets new filename automatically

**Delete Entry**
- Moves entry to backup location
- Shows undo toast for 10 seconds
- Can be restored during undo period

### Cleanup Operations

**Empty Entry Cleanup:**
- Settings → Files & Exports → "Cleanup Empty Entries"
- Removes entries with no content
- Helps keep your data organized

**Automatic Cleanup:**
- Enable "Auto-cleanup empty entries" in Settings
- Automatically removes empty entries on save
- Prevents accumulation of blank files

## Data Portability

### Why Markdown?
- **Universal format**: Readable by any text editor
- **Future-proof**: Plain text will always work
- **Tool-independent**: Not locked to PocketJournal
- **Version control**: Works with Git and other VCS

### Importing from Other Apps
1. Export your data as Markdown or text
2. Place files in the PocketJournal directory structure
3. Add YAML front-matter if desired (optional)
4. Files will appear in PocketJournal automatically

### Migration and Backup

**Full Migration:**
1. Copy entire `Documents/PocketJournal/` folder
2. Install PocketJournal on new system
3. Replace default data folder with your backup
4. All entries and settings preserved

**Selective Migration:**
1. Export specific entries using the export feature
2. Copy exported files to new system
3. Import by placing in PocketJournal directory

## Advanced File Management

### Directory Structure
```
Documents/PocketJournal/
├── Entries/           # Main entry storage
│   ├── 2025/
│   │   ├── 01/       # January entries
│   │   ├── 02/       # February entries
│   │   └── .../
│   └── 2024/
├── Exports/          # Exported files
├── Backups/          # Deleted entry backups
└── .settings/        # Application settings
```

### File Permissions
- PocketJournal needs read/write access to data directory
- Files are created with standard user permissions
- No special administrative access required

### Troubleshooting Files

**Can't save entries?**
- Check data directory permissions
- Ensure sufficient disk space
- Verify directory path in Settings
- Try [Copy Data Folder Path](#copy-data-folder-path) to check location

**Missing entries?**
- Check if data directory changed
- Look in recent entries list
- Use [Open Data Folder](#open-data-folder) to browse files
- Search by filename in file explorer

**Corrupted entries?**
- Check `.bak` backup files (if enabled)
- Open file in text editor to inspect content
- Restore from system backup if available

**Export not working?**
- Check export directory permissions
- Verify export format is supported
- Try different export location

## Helper Actions

### Quick Links
- [Copy Data Folder Path](#copy-data-folder-path) - Copy folder path to clipboard
- [Open Data Folder](#open-data-folder) - Open data folder in file explorer
- [Reset formatting to defaults](#reset-formatting) - Restore default formatting rules

### File System Tips

**Organize by Project:**
- Use descriptive first lines for better organization
- Consider date-based searches for time-related grouping
- Use export feature to create project-specific collections

**Regular Maintenance:**
- Enable automatic backup files
- Periodically export important entries
- Clean up empty entries regularly
- Archive old entries if storage becomes an issue

**Next:** Learn about [Settings](settings.md) to customize your PocketJournal experience.