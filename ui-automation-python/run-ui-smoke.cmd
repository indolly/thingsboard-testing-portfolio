@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] UI virtual environment does not exist.
  echo Create it with: py -3.12 -m venv .venv
  exit /b 2
)

if not defined SE_CACHE_PATH set "SE_CACHE_PATH=D:\toolsoft\selenium-cache"
if not exist "%SE_CACHE_PATH%" mkdir "%SE_CACHE_PATH%"
if not exist "reports" mkdir "reports"
if exist "reports\pytest-results.xml" del /q "reports\pytest-results.xml"
if exist "reports\screenshots" rmdir /s /q "reports\screenshots"

.venv\Scripts\python.exe -m pytest -v tests ^
  -p no:cacheprovider ^
  --junitxml=reports\pytest-results.xml ^
  --alluredir=allure-results --clean-alluredir

exit /b %ERRORLEVEL%
