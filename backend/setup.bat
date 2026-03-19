@echo off
REM Quick start script for Education Tutor Backend (Windows)

echo ======================================
echo 📚 Education Tutor Backend Setup
echo ======================================
echo.

REM Check Python
echo ✓ Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.8+ required
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo ✓ Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo ✓ Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ======================================
echo ✅ Setup Complete!
echo ======================================
echo.
echo To start the server, run:
echo   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo API will be available at:
echo   http://localhost:8000
echo.
echo Documentation:
echo   http://localhost:8000/docs
echo.
echo To run tests:
echo   python tests\test_api.py
echo.
echo To run evaluation:
echo   python experiments\baseline_vs_pruned.py
echo.
pause
