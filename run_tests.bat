@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python -m unittest discover -s tests -v
) else (
  py -3.12 -m unittest discover -s tests -v
  if errorlevel 1 py -3.11 -m unittest discover -s tests -v
)
if errorlevel 1 exit /b 1
exit /b 0
