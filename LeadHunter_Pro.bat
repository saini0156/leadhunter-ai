@echo off
setlocal enabledelayedexpansion
title LeadHunter AI - Master Control Center
cd /d "%~dp0"
color 0B

:MENU
cls
echo ==============================================================================
echo                      LEADHUNTER AI - MASTER CONTROL CENTER
echo       Autonomous AI Lead Generation & Outreach Engine for Local Businesses
echo ==============================================================================
echo.
echo  [1]  Launch Web Control Center (Port 8500 + Auto-Open Browser)
echo  [2]  Run Full End-to-End Pipeline (Discovery, Scoring, Demos, Outreach)
echo  [3]  Run Lead Discovery Only (SerpAPI Google Maps)
echo  [4]  Start Demo Preview Server Only (Port 8000)
echo  [5]  Run Automated Follow-Up Engine
echo  [6]  Sync All Leads to Google Sheets
echo  [7]  Run Automated Test Suite (56 Tests)
echo  [8]  Exit
echo.
echo ==============================================================================
set /p CHOICE="Select an option (1-8): "

if "%CHOICE%"=="1" goto WEB
if "%CHOICE%"=="2" goto PIPELINE
if "%CHOICE%"=="3" goto DISCOVER
if "%CHOICE%"=="4" goto DEMO_SERVER
if "%CHOICE%"=="5" goto FOLLOWUPS
if "%CHOICE%"=="6" goto SYNC
if "%CHOICE%"=="7" goto TESTS
if "%CHOICE%"=="8" goto EXIT

echo.
echo [!] Invalid selection. Please choose 1 to 8.
timeout /t 2 >nul
goto MENU

:WEB
cls
echo ==============================================================================
echo  Starting LeadHunter Web Control Center on http://localhost:8500 ...
echo ==============================================================================
start "" http://localhost:8500
python main.py --web --port 8500
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Web server stopped or encountered an error.
)
pause
goto MENU

:PIPELINE
cls
echo ==============================================================================
echo  RUN FULL LEAD GENERATION PIPELINE
echo ==============================================================================
echo.
set /p TARGET_CITY="Enter target city (default: Chandigarh): "
if "!TARGET_CITY!"=="" set TARGET_CITY=Chandigarh

set /p TARGET_TYPE="Enter business category (default: restaurants): "
if "!TARGET_TYPE!"=="" set TARGET_TYPE=restaurants

set /p MAX_NUM="Enter number of leads to process (default: 5): "
if "!MAX_NUM!"=="" set MAX_NUM=5

echo.
echo Launching autonomous pipeline for "!TARGET_TYPE!" in "!TARGET_CITY!" (Max: !MAX_NUM!)...
echo.
python main.py --city "!TARGET_CITY!" --type "!TARGET_TYPE!" --max !MAX_NUM!
echo.
echo ==============================================================================
echo Pipeline execution complete.
echo ==============================================================================
pause
goto MENU

:DISCOVER
cls
echo ==============================================================================
echo  RUN SERPAPI BUSINESS DISCOVERY
echo ==============================================================================
echo.
set /p DISC_CITY="Enter city: "
set /p DISC_TYPE="Enter category: "
set /p DISC_MAX="Enter max results (default: 5): "
if "!DISC_MAX!"=="" set DISC_MAX=5

python -c "from discovery.serpapi_search import discover_leads; leads = discover_leads('!DISC_CITY!', '!DISC_TYPE!', max_results=!DISC_MAX!); print(f'Discovered {len(leads)} leads.')"
echo.
pause
goto MENU

:DEMO_SERVER
cls
echo ==============================================================================
echo  Starting Demo Preview Server on http://localhost:8000 ...
echo ==============================================================================
start "" http://localhost:8000
python demo/server.py
echo.
pause
goto MENU

:FOLLOWUPS
cls
echo ==============================================================================
echo  RUNNING AUTOMATED FOLLOW-UP LIFECYCLE ENGINE
echo ==============================================================================
echo.
python main.py --followups
echo.
pause
goto MENU

:SYNC
cls
echo ==============================================================================
echo  SYNCING LEADS TO GOOGLE SHEETS
echo ==============================================================================
echo.
python -c "import importlib.util, os; _s = os.path.abspath('logging/sheets_logger.py'); _sp = importlib.util.spec_from_file_location('sh', _s); _m = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_m); from database import Database; db = Database(); leads = db.get_all_leads(); logger = _m.GoogleSheetsLogger(); res = logger.sync_leads(leads); print('Sync Complete:', res)"
echo.
pause
goto MENU

:TESTS
cls
echo ==============================================================================
echo  RUNNING COMPLETE TEST SUITE
echo ==============================================================================
echo.
python -m unittest discover tests
echo.
pause
goto MENU

:EXIT
echo Exiting LeadHunter AI. Goodbye!
timeout /t 1 >nul
exit /b 0
