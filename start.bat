@echo off
setlocal EnableExtensions

title Trading Dashboard Launcher
cd /d "%~dp0"

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"
set "PYTHON=%VENV%\Scripts\python.exe"
set "REQ=%ROOT%requirements.txt"

if not exist "%REQ%" (
    echo.
    echo ERROR: requirements.txt not found.
    echo Expected:
    echo %REQ%
    echo.
    echo Make sure you run this start.bat from the extracted TradingDashboard folder.
    pause
    exit /b 1
)

echo ==========================================
echo       TRADING DASHBOARD
echo ==========================================
echo.

echo [1/4] Checking Python environment...
if not exist "%PYTHON%" (
    echo Creating Python environment...
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv "%VENV%"
    ) else (
        where python >nul 2>&1
        if errorlevel 1 (
            echo.
            echo ERROR: Python 3.10+ is not installed or not in PATH.
            echo Install Python 3.10+ and try again.
            pause
            exit /b 1
        )
        python -m venv "%VENV%"
    )
    if not exist "%PYTHON%" (
        echo.
        echo ERROR: Could not create .venv.
        pause
        exit /b 1
    )
) else (
    echo Python environment already exists.
)

echo.
echo [2/4] Checking dependencies...
"%PYTHON%" -m pip install --disable-pip-version-check -r "%REQ%"
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [3/4] Starting servers...
start "Trading Dashboard Backend" cmd /k "cd /d "%ROOT%" && "%PYTHON%" -m uvicorn Backend.api.main:app --reload"

timeout /t 2 /nobreak >nul

start "Trading Dashboard Frontend" cmd /k "cd /d "%ROOT%Frontend" && "%PYTHON%" -m http.server 5500"

timeout /t 2 /nobreak >nul

echo.
echo [4/4] Opening Dashboard...
start "" "http://127.0.0.1:5500/index.html"

echo.
echo ==========================================
echo       DASHBOARD STARTED
echo ==========================================
echo Frontend: http://127.0.0.1:5500
echo Backend : http://127.0.0.1:8000
echo.
echo Close the Backend and Frontend windows to stop the servers.
echo ==========================================

exit /b 0
