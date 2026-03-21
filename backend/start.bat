@echo off
title EduSarthi Backend
echo ===========================================
echo  EduSarthi Backend  –  Starting up...
echo ===========================================

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
) else (
    echo [WARN] No venv found – using system Python
)

REM Load .env file
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "line=%%A"
        if not "!line:~0,1!"=="#" if not "%%A"=="" (
            set "%%A=%%B"
        )
    )
    echo [OK] .env loaded
)

REM Check python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

REM Install/check dependencies (silent)
pip install -q fastapi uvicorn[standard] pydantic python-multipart python-dotenv

echo.
echo  Backend:   http://localhost:8000
echo  API docs:  http://localhost:8000/docs
echo  Health:    http://localhost:8000/api/health
echo.
echo  Works OFFLINE without any API key.
echo  Set CLAUDE_API_KEY in .env for AI-powered answers.
echo.
echo  Press Ctrl+C to stop.
echo ===========================================

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
