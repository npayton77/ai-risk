@echo off
REM Windows batch script for listing questions in the AI Risk Assessment system

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run from the project root directory.
    pause
    exit /b 1
)

REM Activate virtual environment and run question manager
call venv\Scripts\activate.bat && python question_manager.py list

pause
