"""
Build script for PocketJournal.

This script handles building the application for distribution.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main build function."""
    project_root = Path(__file__).parent.parent
    
    print("PocketJournal Build Script")
    print("=" * 30)
    print(f"Project root: {project_root}")
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    # Check if virtual environment is activated
    if sys.prefix == sys.base_prefix:
        print("\n⚠️  Warning: Virtual environment not detected")
        print("   Consider activating your virtual environment first")
    
    # Install/upgrade build tools
    if not run_command("pip install --upgrade build wheel", "Installing build tools"):
        return 1
    
    # Install development dependencies
    if not run_command("pip install -e .", "Installing package in development mode"):
        return 1
    
    # Run tests
    if not run_command("pytest", "Running tests"):
        print("⚠️  Tests failed, but continuing with build...")
    
    # Clean previous builds
    import shutil
    for dir_name in ["build", "dist"]:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"✓ Cleaned {dir_name} directory")
    
    # Build package
    if not run_command("python -m build", "Building package"):
        return 1
    
    print("\n🎉 Build completed successfully!")
    print(f"Distribution files are in: {project_root / 'dist'}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())