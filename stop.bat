@echo off
setlocal

set "PORT=8000"
set "PID="

for /f "tokens=5" %%a in ('netstat -ano ^| findstr /r /c:":%PORT% .*LISTENING"') do (
  set "PID=%%a"
  goto :found
)

echo [INFO] No listening process found on port %PORT%.
exit /b 0

:found
echo Stopping process %PID% on port %PORT%...
taskkill /PID %PID% /F
if errorlevel 1 (
  echo [ERROR] Failed to stop process %PID%.
  exit /b 1
)

echo [OK] Stopped process %PID%.
exit /b 0
