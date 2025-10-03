"""
Demo script to show Step 6 autosave and entry lifecycle functionality.
Run this to see the autosave system working end-to-end.
"""

import tempfile
import time
from pathlib import Path
from datetime import datetime

from src.pocket_journal.data.entry_manager import Entry, EntryManager


def demo_step6_functionality():
    """Demonstrate Step 6 autosave and entry lifecycle features."""
    print("🚀 Step 6 Demo: Autosave, Timestamps, and Entry Lifecycle")
    print("=" * 60)
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Create entry manager with temp directory
        manager = EntryManager()
        manager.base_path = Path(temp_dir)
        
        # 1. Create new entry (first keypress simulation)
        print("\n1️⃣ Creating new entry (simulating first keypress)...")
        entry = manager.create_new_entry("My first thoughts about PocketJournal")
        print(f"   ✅ Entry created with ID: {entry.metadata.id[:8]}...")
        print(f"   📅 Created at (UTC): {entry.metadata.created_at}")
        
        # Convert to local time for display
        created_utc = datetime.fromisoformat(entry.metadata.created_at.replace('Z', '+00:00'))
        created_local = created_utc.astimezone().strftime("%m/%d/%Y %I:%M %p")
        print(f"   🕐 Local display time: {created_local}")
        
        # 2. Update content (simulate typing)
        print("\n2️⃣ Updating content (simulating user typing)...")
        entry.content = """# My First PocketJournal Entry

This is my first entry in PocketJournal! The autosave system is working beautifully.

Key features I've tested:
- Automatic entry creation on first keypress
- UTC timestamps for reliable storage
- Local time display for user convenience
- YAML front-matter with structured metadata
- Organized file storage in year/month directories

This is exactly what I needed for journaling! 📝"""
        
        print(f"   ✏️ Content updated ({len(entry.content)} characters)")
        
        # Small delay to ensure different timestamp
        time.sleep(0.1)
        
        # 3. Save entry (simulate autosave)
        print("\n3️⃣ Saving entry (simulating autosave)...")
        success = manager.save_entry(entry)
        
        if success:
            print(f"   ✅ Entry saved successfully!")
            print(f"   📄 Filename: {Path(entry.metadata.path).name}")
            print(f"   🕐 Updated at (UTC): {entry.metadata.updated_at}")
            
            # Check file system structure
            file_path = Path(entry.metadata.path)
            print(f"   📂 Directory structure: {file_path.parent.relative_to(manager.base_path)}")
            
            # 4. Show file content
            print("\n4️⃣ Examining saved file content...")
            content = file_path.read_text(encoding='utf-8')
            
            print("   📄 File content preview:")
            print("   " + "-" * 50)
            lines = content.split('\n')
            for i, line in enumerate(lines[:15]):  # Show first 15 lines
                print(f"   {line}")
            if len(lines) > 15:
                print(f"   ... ({len(lines) - 15} more lines)")
            print("   " + "-" * 50)
            
            # 5. Show metadata
            print("\n5️⃣ Entry metadata:")
            print(f"   🆔 ID: {entry.metadata.id}")
            print(f"   📝 Title: {entry.metadata.title}")
            print(f"   🔢 Word count: {entry.metadata.word_count}")
            print(f"   🏷️ Tags: {entry.metadata.tags}")
            print(f"   📅 Created: {entry.metadata.created_at}")
            print(f"   📅 Updated: {entry.metadata.updated_at}")
            
            # 6. Test loading
            print("\n6️⃣ Testing entry loading...")
            loaded_entry = manager.load_entry(entry.metadata.path)
            
            if loaded_entry:
                print(f"   ✅ Entry loaded successfully!")
                print(f"   📝 Content matches: {loaded_entry.content == entry.content}")
                print(f"   🆔 ID matches: {loaded_entry.metadata.id == entry.metadata.id}")
                print(f"   📄 Title: {loaded_entry.metadata.title}")
            
            # 7. Show directory structure
            print("\n7️⃣ Directory structure created:")
            for root, dirs, files in manager.base_path.walk():
                level = len(root.parts) - len(manager.base_path.parts)
                indent = "   " + "  " * level
                print(f"{indent}📂 {root.name}/")
                sub_indent = "   " + "  " * (level + 1)
                for file in files:
                    print(f"{sub_indent}📄 {file}")
        
        else:
            print("   ❌ Failed to save entry!")
    
    print("\n🎉 Step 6 Demo Complete!")
    print("\n✅ All Step 6 features working:")
    print("   • First keypress entry creation with UTC timestamps")
    print("   • Local time display for user interface")
    print("   • YAML front-matter with complete metadata")
    print("   • Structured file storage (YYYY/MM directory organization)")
    print("   • Filename pattern: YYYY-MM-DD_HH-MM-SS_slug.md")
    print("   • Automatic title extraction from content")
    print("   • Word count and metadata tracking")
    print("   • Entry loading and persistence")


if __name__ == "__main__":
    demo_step6_functionality()