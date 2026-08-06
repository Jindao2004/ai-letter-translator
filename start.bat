@echo off
cd /d "%~dp0"
where pythonw.exe >nul 2>nul
if not errorlevel 1 goto use_pythonw
where pyw.exe >nul 2>nul
if not errorlevel 1 goto use_pyw
echo Python 3 was not found. Please install Python 3 first.
pause
exit /b 1

:use_pythonw
start "" pythonw.exe "%~dp0main.py"
exit /b 0

:use_pyw
start "" pyw.exe -3 "%~dp0main.py"
exit /b 0
