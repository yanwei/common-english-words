@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  echo [ERROR] Missing Python virtual environment at:
  echo %PYTHON_EXE%
  echo.
  pause
  exit /b 1
)

start "" http://localhost:8000
"%PYTHON_EXE%" "%~dp0server.py"

endlocal
