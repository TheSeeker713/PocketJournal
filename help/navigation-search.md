# Navigation & Search

PocketJournal provides powerful tools to quickly find and navigate between your entries, even with thousands of notes.

## Quick Search (Ctrl+K)

### Lightning-Fast Search
- Press `Ctrl+K` from anywhere in the app
- Start typing to see instant results
- Search completes in under 200ms even with 1000+ entries

### What Gets Searched
- **Entry titles** and metadata
- **First ~1000 characters** of content
- **Front-matter** (YAML metadata)
- **Date and time** information

### Search Features
- **Relevance scoring**: Best matches appear first
- **Live preview**: See content snippets in results
- **Keyboard navigation**: Use arrow keys to navigate results
- **Quick open**: Press Enter to open selected entry

### Search Tips
```
💡 Search Examples:
"meeting" → Finds all entries mentioning meetings
"2025-10" → Finds entries from October 2025
"important" → Finds entries with IMPORTANT: tags
"action" → Finds entries with ACTION: items
```

## Recent Entries

### Quick Access
- **Hover** over the corner launcher
- See your **last 10 entries** instantly
- **Click** any entry to open it immediately

### Recent Entry Display
- **Title** (first sentence of entry)
- **Timestamp** (when last modified)
- **Preview text** (snippet of content)

### Smart Recency
Entries appear in recent list when:
- Newly created
- Recently modified
- Recently opened

## Navigation Shortcuts

### Global Access
- `Ctrl+Alt+J` - Show/hide PocketJournal (global hotkey)
- `F1` - Open help center (you're here now!)

### Within the App
- `Ctrl+K` - Open search dialog
- `Ctrl+N` - Create new entry
- `Ctrl+S` - Force save current entry
- `Ctrl+,` - Open settings
- `Esc` - Close current dialog/panel

### In Search Dialog
- `↑/↓` - Navigate search results
- `Enter` - Open selected entry
- `Esc` - Close search dialog

### Entry Management
- `Ctrl+Shift+D` - Duplicate current entry
- `Ctrl+E` - Export current entry
- Click **⋯** button for more actions

## Advanced Navigation

### Entry Actions Menu (⋯)
Click the three-dots menu for:
- **View in folder** - Open file location
- **Rename** - Change entry filename
- **Duplicate** - Create a copy
- **Export** - Save as Markdown/Text
- **Delete** - Remove entry (with undo option)

### File System Integration
- Entries stored in organized folders by date
- Standard Markdown format for portability
- Direct file access when needed

### Search Performance

**Optimized for Speed:**
- In-memory search index
- Incremental result updates
- Relevance-based ranking
- Sub-200ms response time

**Search Algorithm:**
1. **Title matching** (highest priority)
2. **Content keyword matching**
3. **Metadata matching**
4. **Fuzzy matching** for typos

## Organization System

### Automatic Organization
Entries are automatically organized by:
- **Year** → `YYYY/`
- **Month** → `MM/`
- **Filename** → `YYYY-MM-DD_HH-MM-SS_title-slug.md`

### Folder Structure
```
Documents/PocketJournal/
├── Entries/
│   ├── 2025/
│   │   ├── 10/
│   │   │   ├── 2025-10-03_14-30-15_my-first-note.md
│   │   │   └── 2025-10-03_15-45-22_meeting-notes.md
│   │   └── 11/
│   └── Exports/
├── Backups/
└── Settings/
```

### Data Portability
- All entries are standard Markdown
- YAML front-matter for metadata
- No proprietary formats
- Easy to backup and migrate

## Tips for Better Navigation

### Use Descriptive First Lines
- Your first sentence becomes the title
- Make it descriptive for better search results
- Example: "Meeting with Sarah about project timeline"

### Leverage Formatting for Search
- Use "IMPORTANT:", "NOTE:", "ACTION:" prefixes
- These become searchable keywords
- Help categorize and find entries later

### Regular Cleanup
- Use Settings → Files & Exports → "Cleanup Empty Entries"
- Export important entries for long-term storage
- Archive old entries if needed

## Troubleshooting

**Search not finding entries?**
- Check if entry exists in recent list
- Try partial words or different terms
- Use [Open Data Folder](#open-data-folder) to verify files

**Recent entries not updating?**
- Ensure entries are being saved (check autosave indicator)
- Try creating a new entry to refresh the list

**Slow search performance?**
- Check Settings → Help & Support → Diagnostics
- Large number of entries may affect performance
- Consider archiving older entries

**Need to access files directly?**
- Use helper link: [Open Data Folder](#open-data-folder)
- Or Settings → Files & Exports → "Open Entries Folder"

**Next:** Learn about [Files & Exports](files-exports.md) for managing your data.