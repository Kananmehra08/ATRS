@echo off
setlocal enabledelayedexpansion
title ATRS Requirements Research Pipeline (Team On Top)
cd /d "%~dp0"

echo ============================================================
echo   ATRS Requirements Engineering Research Pipeline
echo   Team On Top: Yashika Mehra ^& Shaina Mehra
echo   Universal Zero-Setup Launcher
echo ============================================================
echo.

:: ------------------------------------------------------------
:: 1. Deep Python Detection
:: ------------------------------------------------------------
set "PY_CMD="

:: Check py launcher
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py -3"
    goto :found_python
)

:: Check python on PATH
python --version >nul 2>&1
if %errorlevel% equ 0 (
    :: Verify it is not the Microsoft Store dummy shortcut (exit code 9009 or 0.0.0.0)
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_VER_CHECK=%%v"
    echo !PY_VER_CHECK! | findstr /i "Python 3." >nul 2>&1
    if !errorlevel! equ 0 (
        set "PY_CMD=python"
        goto :found_python
    )
)

:: Check python3 on PATH
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python3"
    goto :found_python
)

:: Check portable python in project folder
if exist "portable_python\python.exe" (
    set "PY_CMD=portable_python\python.exe"
    goto :found_python
)

:: Check common Windows install directories
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set "PY_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
    goto :found_python
)
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    set "PY_CMD=%LocalAppData%\Programs\Python\Python312\python.exe"
    goto :found_python
)
if exist "%LocalAppData%\Programs\Python\Python310\python.exe" (
    set "PY_CMD=%LocalAppData%\Programs\Python\Python310\python.exe"
    goto :found_python
)
if exist "%ProgramFiles%\Python311\python.exe" (
    set "PY_CMD=%ProgramFiles%\Python311\python.exe"
    goto :found_python
)
if exist "%ProgramFiles%\Python312\python.exe" (
    set "PY_CMD=%ProgramFiles%\Python312\python.exe"
    goto :found_python
)
if exist "C:\Python311\python.exe" (
    set "PY_CMD=C:\Python311\python.exe"
    goto :found_python
)
if exist "C:\Python312\python.exe" (
    set "PY_CMD=C:\Python312\python.exe"
    goto :found_python
)

:: Python not found anywhere - offer automated zero-click resolution
echo [NOTICE] Python 3 was not detected on this computer.
echo Would you like to automatically install Python or use the Web Dashboard?
echo.
echo   [1] Auto-install Python 3.11 via Windows winget (Recommended, 1-Click)
echo   [2] Open Interactive Visual Dashboard (No Python needed!)
echo   [3] Open Python official download page
echo   [4] Exit
echo.
set /p no_py_opt="Enter choice [1-4, Default=1]: "
if "!no_py_opt!"=="" set "no_py_opt=1"

if "!no_py_opt!"=="1" (
    echo.
    echo Installing Python 3.11 via winget...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    echo Installation finished. Refreshing PATH...
    set "PY_CMD=py -3"
    goto :found_python
)
if "!no_py_opt!"=="2" (
    start "" "dashboard.html"
    exit /b 0
)
if "!no_py_opt!"=="3" (
    start https://www.python.org/downloads/
    echo Please install Python 3.10+ (Check 'Add Python to PATH') then restart run.bat.
    pause
    exit /b 0
)
exit /b 1

:found_python
echo [1/3] Python Runtime:
%PY_CMD% --version
echo.

:: ------------------------------------------------------------
:: 2. Virtual Environment Verification & Auto-Repair
:: ------------------------------------------------------------
set "NEED_INSTALL="

if exist "venv\Scripts\python.exe" (
    :: Test if this venv is functional on THIS computer
    venv\Scripts\python.exe -c "import sys" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [2/3] Existing 'venv' was created on a different laptop or path.
        echo       Auto-repairing virtual environment for this computer...
        rd /s /q "venv"
        %PY_CMD% -m venv venv
        set "NEED_INSTALL=1"
    ) else (
        echo [2/3] Virtual environment 'venv' verified on this computer.
    )
) else (
    echo [2/3] Creating virtual environment 'venv'...
    %PY_CMD% -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    set "NEED_INSTALL=1"
)

:: ------------------------------------------------------------
:: 3. Package Verification & Auto-Install
:: ------------------------------------------------------------
if not defined NEED_INSTALL (
    venv\Scripts\python.exe -c "import pandas, scipy, sklearn, matplotlib, requests, bs4, anthropic, tabulate" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [3/3] Missing dependencies detected. Auto-installing...
        set "NEED_INSTALL=1"
    )
)

if defined NEED_INSTALL (
    echo [3/3] Installing dependencies from requirements.txt...
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERROR] Dependency installation encountered an issue.
        pause
        exit /b 1
    )
    echo       All dependencies installed successfully!
) else (
    echo [3/3] All dependencies verified and ready!
)

echo.
echo ============================================================
echo   Environment Ready! Select an action:
echo ============================================================
:menu
echo.
echo   [0] Open Interactive Visual Dashboard (in Web Browser)
echo   [1] Run Full Live Pipeline (Steps 1 to 4: Fetch + Generate)
echo   [2] Build Blind Annotation Sheets (Step 5)
echo   [3] Run Statistical Analysis, Tables ^& Figures (Step 6)
echo   [4] Run Demo Test (100%% Offline, No API key needed)
echo   [5] Run Laptop Environment Diagnostics (verify_environment.py)
echo   [6] View Token Usage ^& API Statistics
echo   [7] Open Command Shell inside (venv)
echo   [8] Exit
echo.
set /p opt="Enter choice [0-8]: "

if "%opt%"=="0" (
    echo Opening dashboard.html in your default web browser...
    start "" "dashboard.html"
    goto :menu
)
if "%opt%"=="1" (
    echo.
    echo [Step 1] Selecting candidate records...
    venv\Scripts\python.exe scripts\01_select_records.py data\atrs_records.csv
    echo.
    echo [Step 2] Fetching full record texts from gov.uk...
    venv\Scripts\python.exe scripts\02_fetch_texts.py
    echo.
    echo [Step 3] Completeness scoring ^& sample selection...
    venv\Scripts\python.exe scripts\03_completeness.py
    echo.
    echo [Step 4] Requirement generation (LLM)...
    venv\Scripts\python.exe scripts\04_generate.py
    echo.
    echo Done! Requirements saved to data\requirements.csv
    goto :menu
)
if "%opt%"=="2" (
    echo.
    echo [Step 5] Building blind annotation sheets...
    venv\Scripts\python.exe scripts\05_make_annotation_sheets.py
    goto :menu
)
if "%opt%"=="3" (
    echo.
    echo [Step 6] Running statistical analysis...
    venv\Scripts\python.exe scripts\06_analyze.py
    goto :menu
)
if "%opt%"=="4" (
    echo.
    echo Generating synthetic demo data...
    venv\Scripts\python.exe scripts\make_demo_data.py --data demo_data
    echo.
    echo Building demo annotation sheets...
    venv\Scripts\python.exe scripts\05_make_annotation_sheets.py --data demo_data
    echo.
    echo Running statistical analysis on demo data...
    venv\Scripts\python.exe scripts\06_analyze.py --data demo_data --out demo_outputs
    echo.
    echo Demo Test Complete! Figures and summary saved in demo_outputs\
    goto :menu
)
if "%opt%"=="5" (
    echo.
    venv\Scripts\python.exe verify_environment.py
    goto :menu
)
if "%opt%"=="6" (
    echo.
    venv\Scripts\python.exe -c "import os, pandas as pd; p='data/usage_log.csv'; df=pd.read_csv(p) if os.path.exists(p) else None; print(f'Total Calls: {len(df)} | Input Tokens: {df.input_tokens.sum():,} | Output Tokens: {df.output_tokens.sum():,} | Total Tokens: {df.total_tokens.sum():,}') if df is not None and len(df) else print('No usage logged yet.')"
    goto :menu
)
if "%opt%"=="7" (
    echo.
    echo Activating virtual environment. Type 'exit' to return to menu.
    cmd /k "venv\Scripts\activate.bat"
    goto :menu
)
if "%opt%"=="8" (
    exit /b 0
)

echo Invalid choice, please try again.
goto :menu
