# Smart Formatting

PocketJournal automatically formats your text as you type, making your notes more readable and organized without any manual formatting required.

## How It Works

Smart formatting applies styling rules in real-time based on what you write. The original text remains unchanged — only the display is enhanced.

## Formatting Rules

### Text Emphasis

**ALL-CAPS Words**
- Words in ALL-CAPS (4+ characters) become **bold**
- Example: `IMPORTANT` → **IMPORTANT**

**Emphatic Exclamations**
- Phrases ending with exclamation marks become **bold**
- Example: `This is amazing!` → **This is amazing!**

**Important Phrases**
- Text following "IMPORTANT:" becomes **bold**
- Example: `IMPORTANT: Read this carefully` → IMPORTANT: **Read this carefully**

**Parentheticals**
- Text in parentheses becomes *italic*
- Example: `This is a note (with emphasis)` → This is a note *(with emphasis)*

### Special Lines

**Note Lines**
- Lines starting with "NOTE:" get underlined
- Example: `NOTE: Remember this detail`

**Action Lines**
- Lines starting with "ACTION:" get underlined
- Example: `ACTION: Call the client tomorrow`

### Lists

**Bullet Lists**
- Lines starting with `-` or `*` format as bullet lists
- Automatic indentation and spacing

**Numbered Lists**
- Lines starting with `1.`, `2.`, etc. format as numbered lists
- Maintains proper numbering and spacing

## Customizing Formatting

### Toggle Rules On/Off
1. Open Settings (`Ctrl+,`)
2. Go to the "Formatting" tab
3. Check/uncheck individual rules
4. Changes apply immediately!

### Bulk Controls
- **Enable All**: Turn on all formatting rules
- **Disable All**: Turn off all formatting rules
- **Reset**: Restore default formatting settings

## Advanced Features

### Title & Subtitle Detection
- **First sentence** → Automatically becomes the entry title
- **Second sentence** → Becomes the subtitle
- Updates metadata for search and organization

### Live Preview
Formatting applies instantly as you type:
- No need to "compile" or "render"
- What you see is what you get
- Raw text remains unchanged for export

### Session Persistence
Your formatting preferences:
- Save automatically
- Apply to all new entries
- Respect per-rule settings

## Examples

### Before Smart Formatting:
```
IMPORTANT: Team meeting at 3 PM

NOTE: Bring the quarterly reports
ACTION: Email the agenda to everyone

Topics to discuss:
- Budget review
- New project timeline
- URGENT: Client feedback

This meeting is crucial (especially for Q4 planning)!
```

### After Smart Formatting:
**IMPORTANT:** **Team meeting at 3 PM**

<u>NOTE: Bring the quarterly reports</u>  
<u>ACTION: Email the agenda to everyone</u>

Topics to discuss:
• Budget review
• New project timeline  
• **URGENT:** **Client feedback**

This meeting is **crucial** *(especially for Q4 planning)*!

## Troubleshooting

**Formatting not working?**
- Check Settings → Formatting tab
- Ensure rules are enabled
- Try typing a test phrase like "IMPORTANT: test"

**Want to disable a specific rule?**
- Go to Settings → Formatting
- Uncheck the unwanted rule
- Changes apply immediately

**Need to reset everything?**
- Settings → Formatting → "Reset Formatting"
- Or use the helper link: [Reset formatting to defaults](#reset-formatting)

**Next:** Learn about [Navigation & Search](navigation-search.md) for finding your entries quickly.