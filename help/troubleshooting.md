# Troubleshooting

Common issues and solutions for PocketJournal. Most problems can be resolved quickly with these troubleshooting steps.

## Quick Fixes

### Most Common Issues
1. **Can't save entries** → Check data directory permissions
2. **Global hotkey not working** → Test in Settings → General
3. **Search not finding entries** → Verify entries exist in recent list
4. **Launcher disappeared** → Restart application
5. **Settings not saving** → Check file permissions

### Emergency Fixes
- **App won't start**: Delete `.settings` folder to reset
- **Corrupted entries**: Check `.bak` backup files
- **Lost data folder**: Use [Copy Data Folder Path](#copy-data-folder-path)
- **Complete reset**: Uninstall, delete data folder, reinstall

## Startup Issues

### Application Won't Start

**Symptoms**: PocketJournal doesn't launch or crashes immediately

**Solutions**:
1. **Check system requirements**:
   - Windows 10+ / macOS 10.15+ / Linux with Qt support
   - Python 3.8+ runtime (usually bundled)
   - Sufficient disk space (50MB+)

2. **Reset settings**:
   ```
   Delete: Documents/PocketJournal/.settings/
   ```

3. **Check data directory**:
   - Ensure Documents folder exists and is writable
   - Try changing data directory in Settings (if accessible)
   - Use [Open Data Folder](#open-data-folder) helper

4. **Run as administrator** (Windows):
   - Right-click PocketJournal → "Run as administrator"
   - May resolve permission issues

**Still not working?**
- Check Windows Event Viewer for error details
- Try portable installation in different folder
- Contact support with system diagnostics

### Launcher Not Visible

**Symptoms**: Corner launcher doesn't appear

**Solutions**:
1. **Check dock mode**: May be set to system tray
2. **Screen resolution**: Launcher may be off-screen
3. **Restart application**: Sometimes fixes positioning
4. **Reset window positions**: Settings → Fun → "Reset Window Positions"

### Startup Performance

**Symptoms**: Slow application startup

**Solutions**:
- **Large entry count**: Consider archiving old entries
- **Network drive**: Move data to local storage
- **Antivirus**: Add PocketJournal to exceptions
- **Disk space**: Ensure sufficient free space

## Entry Management Issues

### Entries Not Saving

**Symptoms**: Changes lost, autosave not working

**Diagnosis**:
1. Check autosave indicator in status bar
2. Verify data directory is writable
3. Ensure sufficient disk space
4. Look for error messages

**Solutions**:
1. **Permission fix**:
   - Windows: Properties → Security → Full Control
   - macOS: `chmod -R 755 ~/Documents/PocketJournal`
   - Linux: `chmod -R 755 ~/Documents/PocketJournal`

2. **Disk space**:
   - Free up disk space (need 10MB+ free)
   - Check if disk is full

3. **Change data directory**:
   - Settings → Files & Exports → "Change..."
   - Select writable location

4. **Manual save**:
   - Try `Ctrl+S` to force save
   - Check if error appears

### Missing Entries

**Symptoms**: Entries disappeared, can't find old notes

**Diagnosis**:
1. Check recent entries list (hover launcher)
2. Use search (`Ctrl+K`) to find by content
3. Check data directory with [Open Data Folder](#open-data-folder)
4. Look for backup files (`.bak` extension)

**Solutions**:
1. **Wrong data directory**:
   - Settings → Files & Exports → check current directory
   - May have changed accidentally

2. **Search by date**:
   - Use `Ctrl+K` and search for date (e.g., "2025-10")
   - Browse file system directly

3. **Restore from backup**:
   - Look in `Backups/` folder
   - Check for `.bak` files in entry folders
   - Restore by copying back to main location

4. **File system check**:
   - Run disk check utility
   - Check for filesystem corruption

### Corrupted Entries

**Symptoms**: Entry won't open, strange characters, format errors

**Solutions**:
1. **Check backup files**:
   - Look for `.bak` file with same name
   - Copy `.bak` over corrupted file

2. **Manual repair**:
   - Open file in text editor
   - Check YAML front-matter syntax
   - Fix any obvious formatting issues

3. **Restore from system backup**:
   - Use system restore point
   - Restore from cloud backup if available

## Search and Navigation Issues

### Search Not Working

**Symptoms**: `Ctrl+K` doesn't find entries, no results

**Diagnosis**:
1. Verify entries exist (check recent list)
2. Try different search terms
3. Check if search dialog opens
4. Look for error messages

**Solutions**:
1. **Rebuild search index**:
   - Restart application
   - Search indexes rebuild automatically

2. **Check file content**:
   - Open entry file directly
   - Verify content exists
   - Check file isn't empty

3. **Try exact matches**:
   - Search for exact phrases from entries
   - Use quotation marks for exact matches

4. **File system issues**:
   - Check file permissions
   - Verify files aren't corrupted

### Recent Entries Not Updating

**Symptoms**: Recent list shows old entries, new entries missing

**Solutions**:
1. **Force refresh**: Restart application
2. **Check autosave**: Ensure entries are actually saving
3. **Clear recent cache**: Restart clears internal cache
4. **Verify file timestamps**: Check if files are actually updated

### Slow Search Performance

**Symptoms**: Search takes longer than 200ms, feels sluggish

**Diagnosis**:
- Use Settings → Help & Support → Diagnostics
- Check number of entries
- Monitor system performance

**Solutions**:
1. **Archive old entries**: Move to separate folder
2. **Check disk performance**: Ensure disk isn't failing
3. **Antivirus exclusion**: Add data folder to exclusions
4. **System resources**: Close other applications

## Settings and Configuration

### Settings Not Saving

**Symptoms**: Changes revert after restart

**Solutions**:
1. **Check permissions**:
   - Ensure `.settings` folder is writable
   - Run as administrator if needed

2. **Reset settings**:
   - Delete `.settings` folder
   - Restart application
   - Reconfigure preferences

3. **Portable mode**:
   - Use application folder for settings
   - Avoid system-restricted locations

### Global Hotkey Issues

**Symptoms**: `Ctrl+Alt+J` doesn't work, hotkey test fails

**Solutions**:
1. **Test in Settings**: Use Test button in General tab
2. **Change combination**: Try different key combination
3. **Check conflicts**: Another app may use same hotkey
4. **Administrative rights**: Some hotkeys need elevated permissions
5. **Platform support**: Verify global hotkeys work on your system

### Theme Not Changing

**Symptoms**: Theme setting doesn't apply

**Solutions**:
1. **Restart application**: Some theme changes need restart
2. **System theme**: Auto mode follows system theme
3. **Graphics drivers**: Update display drivers
4. **Force specific theme**: Use Light or Dark instead of Auto

## File System Issues

### Can't Open Data Folder

**Symptoms**: "Open Data Folder" fails, file explorer errors

**Solutions**:
1. **Manual navigation**:
   - Open file explorer
   - Navigate to `Documents/PocketJournal/`
   - Use [Copy Data Folder Path](#copy-data-folder-path)

2. **Permissions**: Ensure folder exists and is accessible
3. **Drive issues**: Check if drive is connected/mounted
4. **Path length**: Very long paths may cause issues

### Export Not Working

**Symptoms**: Export fails, can't save exported files

**Solutions**:
1. **Check export directory**: Ensure destination is writable
2. **Change export location**: Try different folder
3. **File permissions**: Verify write access to destination
4. **Disk space**: Ensure sufficient space for export
5. **File conflicts**: Check if file already exists

### Backup Files Issues

**Symptoms**: No `.bak` files created, backup system not working

**Solutions**:
1. **Enable in Settings**: Files & Exports → "Create backup files"
2. **Check permissions**: Backup folder must be writable
3. **Disk space**: Backups need additional space
4. **Manual backup**: Copy files manually as backup

## Performance Issues

### High Memory Usage

**Symptoms**: PocketJournal using excessive RAM

**Solutions**:
1. **Restart application**: Clears memory leaks
2. **Large entries**: Very large entries may use more memory
3. **Many entries**: Consider archiving old entries
4. **System resources**: Check overall system memory

### Slow UI Response

**Symptoms**: UI feels sluggish, delayed responses

**Solutions**:
1. **System performance**: Check CPU and memory usage
2. **Graphics drivers**: Update display drivers
3. **Disable animations**: Settings → Fun → disable fun animations
4. **Reduce font size**: Smaller fonts may render faster

### Disk Usage

**Symptoms**: PocketJournal using too much disk space

**Analysis**:
- Each entry is typically 1-5KB
- Backup files double space usage
- Settings and caches are minimal

**Solutions**:
1. **Cleanup empty entries**: Settings → Files & Exports
2. **Remove old backups**: Delete old `.bak` files
3. **Archive entries**: Move old entries to external storage
4. **Disable backups**: Turn off automatic backup files

## System Integration

### Launch at Login Issues

**Symptoms**: App doesn't start with Windows

**Solutions** (Windows only):
1. **Check Settings**: General → "Launch at login"
2. **Registry permissions**: May need admin rights
3. **Windows startup**: Check Task Manager → Startup tab
4. **Manual addition**: Add to Windows startup folder

### System Tray Issues

**Symptoms**: Tray icon missing, tray mode not working

**Solutions**:
1. **System tray availability**: Not all systems support it
2. **Switch to corner mode**: Docking → "Corner Launcher"
3. **Restart explorer**: Restart Windows Explorer process
4. **Check system settings**: Ensure tray icons are enabled

## Getting Help

### Diagnostic Information

**Collect System Info**:
1. Settings → Help & Support → "Refresh Diagnostics"
2. Click "Copy to Clipboard"
3. Include in support requests

**Key Information**:
- Operating system and version
- PocketJournal version
- Python and PySide6 versions
- Data directory location
- Error messages (exact text)

### Helper Links

Use these helper links for quick troubleshooting:
- [Copy Data Folder Path](#copy-data-folder-path) - Get folder path
- [Open Data Folder](#open-data-folder) - Browse entries
- [Reset formatting to defaults](#reset-formatting) - Fix formatting

### Self-Diagnosis Steps

1. **Restart application** - Fixes most temporary issues
2. **Check recent entries** - Verify data is accessible
3. **Test search** - Try `Ctrl+K` with known terms
4. **Review settings** - Check for configuration issues
5. **Check diagnostics** - Use built-in diagnostic tools

### When to Reset

**Reset settings** if:
- Settings won't save
- UI behaves strangely
- Shortcuts not working
- Theme issues

**Reset data** if:
- Entries corrupted beyond repair
- File system issues
- Want fresh start
- Migration to new system

### Support Resources

- **Help Center**: Press `F1` for complete documentation
- **Settings**: `Ctrl+,` for configuration options
- **Diagnostics**: Settings → Help & Support for system info
- **Community**: Check online forums and documentation

**Remember**: Most issues are configuration or permission related. Always try the simple fixes first before more drastic measures.