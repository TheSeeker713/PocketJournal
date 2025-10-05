# Settings

PocketJournal provides comprehensive settings to customize your experience. Access settings with `Ctrl+,` or by clicking the gear icon.

## General Settings

### Appearance
**Theme Selection**
- **Auto (System)**: Follows your system dark/light mode
- **Light**: Always use light theme
- **Dark**: Always use dark theme

*Changes apply immediately without restart.*

### Startup
**Launch at Login**
- Automatically start PocketJournal when you log in
- Available on Windows (registry-based)
- Status indicator shows current state

### Global Hotkey
**System-wide Access**
- Default: `Ctrl+Alt+J`
- Works even when PocketJournal is minimized
- Test button verifies hotkey registration
- Custom combinations supported

*Tip: Use Test button to verify your hotkey works before closing settings.*

## Docking Settings

### Dock Mode
**Corner Launcher** (Default)
- Small circular launcher in screen corner
- Always visible and accessible
- Minimal screen real estate usage

**System Tray**
- Icon appears in system notification area
- More traditional application behavior
- May not be available on all systems

*Note: Dock mode changes require application restart.*

### Corner Launcher Settings
**Circle Size**: 32-64 pixels
- Adjust launcher visibility vs. screen space
- Default: 48px

**Animation Duration**: 100-1000ms
- Speed of expand/collapse animations
- Default: 300ms

### Editor Panel Settings
**Panel Dimensions**
- **Width**: 300-800px (default: 500px)
- **Height**: 400-1000px (default: 600px)

**Auto-focus Editor**
- Automatically focus text editor when panel expands
- Recommended for faster note-taking

## Formatting Settings

### Smart Formatting Rules
Individual toggles for each formatting rule:

**Text Emphasis**
- ✅ **Bold ALL-CAPS words** (≥4 characters)
- ✅ **Bold phrases ending with exclamation marks**
- ✅ **Bold phrases following "IMPORTANT:"**
- ✅ **Italicize text in parentheses**

**Special Lines**
- ✅ **Underline lines starting with "NOTE:"**
- ✅ **Underline lines starting with "ACTION:"**

**Lists**
- ✅ **Format bullet lists** (-, *)
- ✅ **Format numbered lists** (1., 2., etc.)

**Bulk Controls**
- **Enable All**: Turn on all formatting rules
- **Disable All**: Turn off all formatting rules

*All changes apply immediately to the editor.*

### Editor Settings
**Font Configuration**
- **Font Family**: System fonts + custom options
- **Font Size**: 8-24pt (default: 11pt)

**Behavior**
- **Auto-save Delay**: 100-5000ms (default: 500ms)
- **Word Wrap**: Wrap long lines in editor
- **Auto Indent**: Automatically indent new lines

## Files & Exports Settings

### Data Storage
**Data Directory**
- Current location displayed
- Change button to select new location
- Open button to browse current location

**File Management**
- ✅ **Create backup files**: .bak copies before overwriting
- ☐ **Auto-cleanup empty entries**: Remove entries with no content

### Export Configuration
**Default Settings**
- **Export Format**: Markdown (.md), Plain Text (.txt), Rich Text (.rtf)
- **Export Directory**: Custom location or system default

**Export Options**
- ✅ **Include metadata in exports**: YAML front-matter
- ✅ **Preserve formatting in exports**: Smart formatting styles

### File Operations
**Quick Actions**
- **Open Entries Folder**: Browse entry files directly
- **Cleanup Empty Entries**: Remove all empty entries

## Help & Support Settings

### Documentation
**Help Resources**
- **User Guide**: Comprehensive usage documentation
- **Keyboard Shortcuts**: Complete shortcut reference
- **Release Notes**: Version history and changes

### About Information
**Application Details**
- Version information
- Organization details
- Technology stack (PySide6/Qt)

### Diagnostics
**System Information**
- Operating system details
- Python and PySide6 versions
- Current settings summary
- Feature availability status

**Diagnostic Actions**
- **Refresh**: Update diagnostic information
- **Copy to Clipboard**: Copy diagnostics for support
- **Save to File**: Export diagnostics as text file

## Fun Settings

### Easter Eggs
**Master Control**
- ✅ **Enable easter eggs**: Hidden features and surprises
- ✅ **Show easter egg icon in toolbar**: Visual indicator

*Note: Disabling easter eggs also disables the toolbar icon.*

**Fun Features**
- ✅ **Enable fun animations**: Playful UI animations
- ☐ **Enable sound effects**: Audio feedback (experimental)

### Development & Debug
**Advanced Options**
- ☐ **Enable debug mode**: Additional logging and features
- ☐ **Verbose logging**: Detailed console output
- ☐ **Show developer tools**: Advanced debugging options

**Reset Options**
- **Reset Window Positions**: Restore default window layout
- **Reset Formatting**: Restore all formatting rules to defaults

## Settings Management

### Immediate Persistence
- All settings save automatically
- No "Apply" button required
- Changes take effect immediately

### Settings Storage
Settings are stored in:
```
Documents/PocketJournal/.settings/
```

### Backup and Reset
**Manual Backup**
- Copy `.settings` folder
- Includes all preferences and configurations

**Reset to Defaults**
- Settings → "Restore Defaults" button
- Clears all customizations
- Restores factory settings

## Keyboard Shortcuts in Settings

### Navigation
- `Tab` / `Shift+Tab`: Navigate between controls
- `Space`: Toggle checkboxes
- `Enter`: Activate buttons
- `Esc`: Close settings dialog

### Tab Switching
- `Ctrl+Tab`: Next tab
- `Ctrl+Shift+Tab`: Previous tab
- `Ctrl+1-6`: Jump to specific tab

## Troubleshooting Settings

**Settings not saving?**
- Check file permissions in data directory
- Verify settings folder exists and is writable
- Try "Restore Defaults" to reset corrupted settings

**Global hotkey not working?**
- Use Test button in General tab
- Try different key combination
- Check if another app is using the same hotkey
- Verify global hotkey support on your system

**Theme not changing?**
- Restart application if using Auto (System) mode
- Check system theme settings
- Try explicit Light/Dark mode

**Launch at login not working?**
- Windows only feature
- Requires administrative permissions for registry access
- Check Windows startup programs list

**Export settings not applying?**
- Verify export directory exists and is writable
- Check file permissions
- Try different export location

## Advanced Configuration

### Configuration Files
Advanced users can edit configuration files directly:

```
Documents/PocketJournal/.settings/
├── app.conf           # Main application settings
├── formatting.conf    # Formatting rule states
├── window.conf        # Window positions and sizes
└── shortcuts.conf     # Custom keyboard shortcuts
```

**Warning**: Direct editing may cause issues. Use Settings dialog when possible.

### Portable Installation
To make PocketJournal portable:
1. Set data directory to application folder
2. Disable "Launch at login"
3. Use relative paths for exports
4. Backup entire application folder

**Next:** Learn about [Privacy](privacy.md) and data handling in PocketJournal.