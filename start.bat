@echo off
REM Quick Start Script for Fraud Sentinel Agent with Gemini AI
REM Run this after adding your GEMINI_API_KEY to backend\logic\.env

echo ==========================================
echo 🤖 FRAUD SENTINEL AGENT - QUICK START
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Error: Please run this script from the project root directory
    echo    cd C:\path\to\fraud-sentinel-agent
    exit /b 1
)

echo Step 1: Checking Gemini Integration...
cd backend\logic
if exist "verify_gemini.py" (
    python verify_gemini.py
    if errorlevel 1 (
        echo.
        echo ⚠️  Gemini verification failed!
        echo    Please add your GEMINI_API_KEY to backend\logic\.env
        echo    Get it from: https://makersuite.google.com/app/apikey
        cd ..\..
        exit /b 1
    )
) else (
    echo ⚠️  verify_gemini.py not found - skipping verification
)
cd ..\..

echo.
echo ==========================================
echo ✅ All checks passed!
echo ==========================================
echo.
echo To start the system, open 3 terminals:
echo.
echo 📍 Terminal 1 - Auth Server:
echo    cd backend\auth ^&^& npm start
echo.
echo 📍 Terminal 2 - API Server (with Gemini AI):
echo    cd backend\logic ^&^& python main.py
echo.
echo 📍 Terminal 3 - Flutter App:
echo    cd frontend\app ^&^& flutter run
echo.
echo ==========================================
echo 📖 Documentation:
echo    • INTEGRATION_STATUS_REPORT.md - Complete overview
echo    • GEMINI_AI_INTEGRATION.md - Detailed setup
echo    • GEMINI_INTEGRATION_CHECKLIST.md - Step-by-step
echo ==========================================
echo.
echo 🚀 Happy fraud detecting!
echo.
pause
