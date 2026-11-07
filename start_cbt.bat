@echo off
title NCMB - CBT Examination Assessment Platform
color 0A
cd /d "%~dp0"

echo ======================================================================
echo           NCMB CBT EXAMINATION ASSESSMENT PLATFORM - LAUNCHER
echo ======================================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and check 'Add Python to PATH'.
    pause
    exit /b 1
)

:: Run CBT platform
echo Starting NCMB CBT Application Server...
python run_cbt.py

pause
