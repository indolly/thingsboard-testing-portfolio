@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=.venv\Scripts\python.exe"
set "REPORT_DIR=reports"
set "ALLURE_RESULTS=allure-results"
set "ALLURE_REPORT=allure-report"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] Python virtual environment was not found.
  echo Run: python -m venv .venv
  exit /b 2
)

if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"

where allure >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Allure command line was not found in PATH.
  echo Install Allure CLI first, then run: allure --version
  exit /b 3
)

echo ============================================================
echo ThingsBoard Python API Regression
echo ============================================================

"%PYTHON_EXE%" -m pytest ^
  -v ^
  --tb=short ^
  -p no:cacheprovider ^
  --junitxml="%REPORT_DIR%\pytest-results.xml" ^
  --alluredir="%ALLURE_RESULTS%" ^
  --clean-alluredir

set "TEST_EXIT_CODE=%ERRORLEVEL%"

allure generate "%ALLURE_RESULTS%" --clean -o "%ALLURE_REPORT%"
set "ALLURE_EXIT_CODE=%ERRORLEVEL%"

echo.
echo Allure report : %CD%\%ALLURE_REPORT%
echo Allure results: %CD%\%ALLURE_RESULTS%
echo JUnit XML    : %CD%\%REPORT_DIR%\pytest-results.xml
echo View report : allure open "%CD%\%ALLURE_REPORT%"

if not "%ALLURE_EXIT_CODE%"=="0" (
  echo [FAILED] Allure report generation failed. Exit code: %ALLURE_EXIT_CODE%
  exit /b %ALLURE_EXIT_CODE%
)

if not "%TEST_EXIT_CODE%"=="0" (
  echo [FAILED] Regression tests failed. Exit code: %TEST_EXIT_CODE%
) else (
  echo [PASSED] All regression tests passed.
)

exit /b %TEST_EXIT_CODE%

