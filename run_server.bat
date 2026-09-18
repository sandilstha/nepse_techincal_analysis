@echo off
REM Double-click to start the NEPSE platform.
REM Always uses the project's venv Python, so no activation is needed,
REM and stops any old server on the same address first so two never stack.
cd /d "%~dp0"

for /f "tokens=5" %%p in ('netstat -ano ^| findstr "192.168.1.31:8501" ^| findstr LISTENING') do (
    echo Stopping old server, PID %%p
    taskkill /PID %%p /F >nul 2>&1
)

echo Starting server at http://192.168.1.31:8501/
"%~dp0venv\Scripts\python.exe" manage.py runserver 192.168.1.31:8501
pause
