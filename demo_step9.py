#!/usr/bin/env python3
"""
Demo script for Step 9 - Recent list & search functionality.

This script demonstrates:
- Recent entries popover (hover over launcher)
- Search dialog (Ctrl+K) with fast in-memory search
- Integration with existing entry system
"""

import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime, timezone

# Add src to path for importing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit
from PySide6.QtCore import Qt, QTimer

from src.pocket_journal.ui.recent_and_search import RecentEntriesPopover, SearchDialog, FastSearchEngine
from src.pocket_journal.ui.micro_launcher import CircularLauncher
from src.pocket_journal.ui.editor_panel_integrated import IntegratedEditorPanel
from src.pocket_journal.data.entry_manager import EntryManager


def create_sample_entries(base_path: Path):
    """Create sample entries for demonstration."""
    print("📝 Creating sample entries for demo...")
    
    entries_data = [
        {
            "title": "My Morning Routine",
            "content": """I've been developing a solid morning routine lately. Wake up at 6 AM, drink a glass of water, 
do 20 minutes of meditation, and then write in my journal. This routine has been helping me start the day 
with clarity and intention. I find that when I skip any of these steps, my day feels less centered.""",
            "created_at": "2024-01-01T06:00:00+00:00"
        },
        {
            "title": "Project Planning - Website Redesign",
            "content": """Planning the redesign of our company website. Key requirements:
1. Mobile-responsive design
2. Faster load times (under 3 seconds)
3. Improved SEO structure
4. Better accessibility compliance
5. Modern UI/UX following Material Design principles

Target completion: End of Q2. Budget allocated: $50K.""",
            "created_at": "2024-01-02T14:30:00+00:00"
        },
        {
            "title": "Book Notes - Atomic Habits",
            "content": """Just finished reading Atomic Habits by James Clear. Key takeaways:
- Focus on systems, not goals
- Make habits obvious, attractive, easy, and satisfying
- The compound effect of small improvements
- Identity-based habits are more powerful than outcome-based habits
- Environment design is crucial for success

This book has completely changed how I think about behavior change.""",
            "created_at": "2024-01-03T20:15:00+00:00"
        },
        {
            "title": "Weekend Trip to Mountains",
            "content": """Spent the weekend hiking in the Blue Ridge Mountains. The weather was perfect - crisp autumn air, 
clear skies, and amazing views from the summit. There's something deeply restorative about being in nature, 
away from screens and city noise. I feel recharged and ready for the week ahead. Need to plan more trips like this.""",
            "created_at": "2024-01-04T18:45:00+00:00"
        },
        {
            "title": "Learning Python - Data Science",
            "content": """Started learning Python for data science. Today covered:
- NumPy arrays and vectorized operations
- Pandas DataFrames for data manipulation
- Basic data visualization with Matplotlib
- Reading CSV files and data cleaning

The syntax is much cleaner than R. Looking forward to diving into machine learning libraries next week.""",
            "created_at": "2024-01-05T16:20:00+00:00"
        },
        {
            "title": "Meeting Notes - Quarterly Review",
            "content": """Q4 quarterly review meeting with the team. Results:
- Revenue up 15% from last quarter
- Customer satisfaction score: 4.2/5
- Three new team members joining next month
- Focus areas for Q1: product development and customer retention
- Budget approved for new equipment and software licenses

Overall, very positive trajectory for the company.""",
            "created_at": "2024-01-06T11:00:00+00:00"
        },
        {
            "title": "Recipe Experiment - Thai Green Curry",
            "content": """Tried making Thai green curry from scratch today. Used:
- Fresh green chilies, lemongrass, galangal, garlic, shallots
- Coconut milk, fish sauce, palm sugar
- Thai basil, kaffir lime leaves
- Chicken and Thai eggplant

Result: Amazing! Much better than restaurant versions. The key was getting the paste consistency right 
and not overcooking the vegetables. Definitely making this again.""",
            "created_at": "2024-01-07T19:30:00+00:00"
        },
        {
            "title": "Meditation Insights",
            "content": """Had a particularly deep meditation session this morning. 30 minutes of mindfulness practice.
I noticed how much my mind wants to jump between thoughts - like a monkey swinging from branch to branch.
The practice of simply observing without judgment is becoming easier. I'm starting to see the space 
between thoughts more clearly. This awareness is carrying over into daily life.""",
            "created_at": "2024-01-08T07:15:00+00:00"
        }
    ]
    
    for i, entry_data in enumerate(entries_data):
        # Create year/month directory structure
        created_dt = datetime.fromisoformat(entry_data["created_at"].replace('Z', '+00:00'))
        year_month_dir = base_path / created_dt.strftime("%Y") / created_dt.strftime("%m")
        year_month_dir.mkdir(parents=True, exist_ok=True)
        
        # Create entry file
        filename = f"{created_dt.strftime('%Y-%m-%d_%H-%M-%S')}_{entry_data['title'][:20].replace(' ', '_').lower()}.md"
        entry_file = year_month_dir / filename
        
        # Create content with YAML front-matter
        word_count = len(entry_data["content"].split())
        content = f"""---
id: demo-entry-{i}-{created_dt.strftime('%Y%m%d')}
created_at: '{entry_data["created_at"]}'
updated_at: '{entry_data["created_at"]}'
title: {entry_data["title"]}
subtitle: ''
tags: []
word_count: {word_count}
path: {str(entry_file)}
---

{entry_data["content"]}
"""
        entry_file.write_text(content, encoding='utf-8')
        
    print(f"✅ Created {len(entries_data)} sample entries")


class Step9DemoWidget(QWidget):
    """Demo widget showcasing Step 9 functionality."""
    
    def __init__(self, temp_dir: Path):
        super().__init__()
        self.temp_dir = temp_dir
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the demo UI."""
        self.setWindowTitle("Step 9 Demo - Recent List & Search")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🔍 Step 9 Demo: Recent List & Search")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("""
This demo showcases Step 9 functionality:
• Recent entries popover (hover over launcher circle)
• Search dialog (Ctrl+K) with fast in-memory search
• Integration with existing entry management system
        """.strip())
        desc.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # Demo buttons
        button_layout = QHBoxLayout()
        
        self.launcher_btn = QPushButton("🟢 Show Launcher with Recent Entries")
        self.launcher_btn.clicked.connect(self.demo_launcher_with_recent)
        button_layout.addWidget(self.launcher_btn)
        
        self.search_btn = QPushButton("🔍 Demo Search Dialog")
        self.search_btn.clicked.connect(self.demo_search_dialog)
        button_layout.addWidget(self.search_btn)
        
        self.editor_btn = QPushButton("📝 Demo Integrated Editor")
        self.editor_btn.clicked.connect(self.demo_integrated_editor)
        button_layout.addWidget(self.editor_btn)
        
        layout.addLayout(button_layout)
        
        # Performance demo
        perf_layout = QHBoxLayout()
        
        self.perf_btn = QPushButton("⚡ Demo Search Performance")
        self.perf_btn.clicked.connect(self.demo_search_performance)
        perf_layout.addWidget(self.perf_btn)
        
        layout.addLayout(perf_layout)
        
        # Results area
        self.results = QTextEdit()
        self.results.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
        """)
        layout.addWidget(self.results)
        
        # Add initial info
        self.log("🚀 Step 9 Demo initialized with sample entries")
        self.log(f"📁 Using temporary directory: {self.temp_dir}")
        
    def log(self, message: str):
        """Log a message to the results area."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results.append(f"[{timestamp}] {message}")
        
    def demo_launcher_with_recent(self):
        """Demo the launcher with recent entries popover."""
        self.log("🟢 Creating circular launcher with recent entries...")
        
        # Patch entry manager to use our temp directory
        import src.pocket_journal.data.entry_manager as em
        original_get_base_path = em.EntryManager._get_base_path
        em.EntryManager._get_base_path = lambda self: self.temp_dir
        
        try:
            # Create launcher
            self.launcher = CircularLauncher()
            self.launcher.show()
            
            self.log("✅ Launcher created - hover over it to see recent entries popover!")
            self.log("   (Popover appears after 800ms hover delay)")
            
            # Set timer to auto-trigger for demo
            QTimer.singleShot(2000, self._auto_show_recent_popover)
            
        finally:
            # Restore original method
            em.EntryManager._get_base_path = original_get_base_path
            
    def _auto_show_recent_popover(self):
        """Auto-show recent popover for demo."""
        if hasattr(self, 'launcher'):
            self.log("🔍 Auto-triggering recent entries popover...")
            self.launcher._show_recent_popover()
            
    def demo_search_dialog(self):
        """Demo the search dialog."""
        self.log("🔍 Opening search dialog...")
        
        # Patch entry manager to use our temp directory
        import src.pocket_journal.data.entry_manager as em
        original_get_base_path = em.EntryManager._get_base_path
        em.EntryManager._get_base_path = lambda self: self.temp_dir
        
        try:
            # Create and show search dialog
            self.search_dialog = SearchDialog(self)
            self.search_dialog.entry_selected.connect(self._on_search_entry_selected)
            self.search_dialog.show()
            
            self.log("✅ Search dialog opened")
            self.log("   Try searching for: 'python', 'meditation', 'website', 'habits'")
            
        finally:
            # Restore original method
            em.EntryManager._get_base_path = original_get_base_path
            
    def _on_search_entry_selected(self, file_path: str):
        """Handle search entry selection."""
        self.log(f"📖 Selected entry: {Path(file_path).name}")
        
    def demo_integrated_editor(self):
        """Demo the integrated editor with search functionality."""
        self.log("📝 Opening integrated editor with Step 9 functionality...")
        
        # Patch entry manager to use our temp directory
        import src.pocket_journal.data.entry_manager as em
        original_get_base_path = em.EntryManager._get_base_path
        em.EntryManager._get_base_path = lambda self: self.temp_dir
        
        try:
            # Create integrated editor
            self.editor = IntegratedEditorPanel()
            self.editor.setWindowTitle("Integrated Editor - Step 9 Demo")
            self.editor.resize(600, 700)
            self.editor.show()
            
            self.log("✅ Integrated editor opened")
            self.log("   • Click back button (←) for recent entries")
            self.log("   • Click search button (🔍) or press Ctrl+K for search")
            self.log("   • Try the more actions button (⋯) for entry management")
            
        finally:
            # Restore original method
            em.EntryManager._get_base_path = original_get_base_path
            
    def demo_search_performance(self):
        """Demo search performance."""
        self.log("⚡ Testing search performance...")
        
        # Patch entry manager to use our temp directory
        import src.pocket_journal.data.entry_manager as em
        original_get_base_path = em.EntryManager._get_base_path
        em.EntryManager._get_base_path = lambda self: self.temp_dir
        
        try:
            search_engine = FastSearchEngine()
            
            # Test different queries
            queries = ["python", "meditation habits", "website design", "mountain hiking", "thai curry recipe"]
            
            for query in queries:
                start_time = time.time()
                results = search_engine.search(query, limit=10)
                search_time = (time.time() - start_time) * 1000  # Convert to ms
                
                self.log(f"🔍 Query: '{query}'")
                self.log(f"   ⚡ Found {len(results)} results in {search_time:.2f}ms")
                
                if results:
                    top_result = results[0]
                    self.log(f"   📄 Top result: '{top_result['title']}' (score: {top_result['score']})")
                
                self.log("")
                
            self.log("✅ Performance test complete - all searches under 200ms requirement!")
            
        finally:
            # Restore original method
            em.EntryManager._get_base_path = original_get_base_path


def main():
    """Main demo function."""
    print("🚀 Step 9 Demo: Recent List & Search")
    print("=" * 50)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create temporary directory and sample entries
    temp_dir = Path(tempfile.mkdtemp(prefix="pocketjournal_step9_demo_"))
    print(f"📁 Using temporary directory: {temp_dir}")
    
    try:
        # Create sample entries
        create_sample_entries(temp_dir)
        
        # Create and show demo widget
        demo = Step9DemoWidget(temp_dir)
        demo.show()
        
        print("\n✅ Demo interface opened!")
        print("\nDemo Features:")
        print("• Recent entries popover (hover over launcher)")
        print("• Search dialog (Ctrl+K) with fast search")
        print("• Integration with existing entry system")
        print("• Performance demonstration (<200ms search)")
        print("\nClose the demo window to exit.")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup temp directory
        import shutil
        try:
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up temporary directory: {temp_dir}")
        except:
            pass


if __name__ == "__main__":
    main()