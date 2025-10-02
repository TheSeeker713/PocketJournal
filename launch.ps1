# PowerShell launch script for PocketJournal
Write-Host "Starting PocketJournal..." -ForegroundColor Green

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Activate virtual environment and run the application
& "$ScriptDir\venv\Scripts\Activate.ps1"
& "$ScriptDir\venv\Scripts\python.exe" -m pocket_journal

Write-Host "PocketJournal has exited." -ForegroundColor Yellow
Read-Host "Press Enter to continue..."