# PocketJournal

## ⚠️ DEVELOPMENT WARNING
**This application is currently in active development and may contain bugs, incomplete features, or unexpected behavior. Use at your own discretion. Data loss or application crashes may occur. Please backup any important journal entries.**

---

A Windows-first personal journaling application built with PySide6.

## What's New

📋 **[View Changelog](about/changelog.md)** - See what's new in the latest version and track development progress.

## Features

- Clean, intuitive interface optimized for Windows
- Markdown support for rich text formatting
- Fast search and organization
- Data stored locally with privacy in mind
- Lightweight and responsive

## Requirements

- Python 3.10 or higher
- Windows 10/11 (primary target platform)

## Installation & Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd PocketJournal
```

### 2. Create and activate virtual environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# Or for Command Prompt
# .\venv\Scripts\activate.bat
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install the package in development mode
```bash
pip install -e .
```

## Running the Application

### Method 1: Using the installed script
```bash
pocket-journal
```

### Method 2: Using Python module
```bash
python -m pocket_journal
```

### Method 3: Direct execution
```bash
python src/pocket_journal/main.py
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
# Format code with black
black src tests

# Sort imports with isort
isort src tests

# Lint with flake8
flake8 src tests
```

### Building for Distribution
```bash
# Build wheel and source distribution
python -m build

# Install build tools if needed
pip install build
```

## Project Structure

```
PocketJournal/
├── src/
│   └── pocket_journal/          # Main application package
│       ├── __init__.py
│       ├── __main__.py          # Entry point for python -m pocket_journal
│       ├── main.py              # Application main function
│       ├── ui/                  # User interface components
│       ├── core/                # Core business logic
│       ├── data/                # Data handling and storage
│       └── utils/               # Utility functions
├── tests/                       # Test suite
├── assets/                      # Icons, images, etc.
├── help/                        # Help documentation
├── about/                       # About dialog content
├── scripts/                     # Build and deployment scripts
├── requirements.txt             # Project dependencies
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Troubleshooting

### Virtual Environment Issues
If you have trouble activating the virtual environment:
- Ensure you're using PowerShell or Command Prompt as Administrator if needed
- Check that Python is properly installed and in your PATH
- Try using `python -m venv venv --upgrade-deps` when creating the environment

### PySide6 Installation Issues
If PySide6 fails to install:
- Ensure you have the latest pip: `python -m pip install --upgrade pip`
- Try installing PySide6 separately: `pip install PySide6`
- Check that you're using a supported Python version (3.10+)