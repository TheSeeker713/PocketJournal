@echo off
REM Launch script for PocketJournal
echo Starting PocketJournal...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m pocket_journal
pause