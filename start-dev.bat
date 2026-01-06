@echo off
echo Starting AI Pentest Brain Development Environment...
echo.

REM Start Backend in new window
echo Starting Backend API on http://localhost:8000...
start "Backend API" cmd /k "cd backend && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend in new window
echo Starting Frontend on http://localhost:3000...
start "Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ========================================
echo Development servers starting...
echo Backend API: http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo Frontend:    http://localhost:3000
echo ========================================
echo.
echo Close the terminal windows to stop the servers.
pause
