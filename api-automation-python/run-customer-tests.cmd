@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] Python virtual environment was not found.
  echo Run: python -m venv .venv
  exit /b 2
)

"%PYTHON_EXE%" -m pytest tests\test_customers_permissions.py -v -p no:cacheprovider
exit /b %ERRORLEVEL%

