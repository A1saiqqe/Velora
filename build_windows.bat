@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo  Velora Music Player - Windows release
echo ========================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python Launcher was not found.
  echo Install 64-bit Python 3.12 or 3.11 from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

rem requirements.txt supports Python 3.11 and 3.12. Prefer 3.12, then 3.11.
py -3.12 -c "import sys; assert sys.version_info[:2] == (3, 12)" >nul 2>nul
if not errorlevel 1 (
  set "PYVER=3.12"
) else (
  py -3.11 -c "import sys; assert sys.version_info[:2] == (3, 11)" >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Install 64-bit Python 3.12 or 3.11 before building.
    pause
    exit /b 1
  )
  set "PYVER=3.11"
)
echo Using Python %PYVER%...
if not exist ".venv\Scripts\python.exe" py -%PYVER% -m venv .venv
if errorlevel 1 goto :failed

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 goto :failed
python -m pip install -r requirements-build.txt
if errorlevel 1 goto :failed

echo.
echo Running automated tests...
python -m unittest discover -s tests -v
if errorlevel 1 goto :failed

if exist build rmdir /s /q build
if exist dist\Velora rmdir /s /q dist\Velora
if exist Velora.spec del /q Velora.spec

echo.
echo Building the application...
python -m PyInstaller --noconfirm --clean --windowed --onedir --name Velora ^
  --collect-all customtkinter ^
  --collect-all pygame ^
  --hidden-import=mutagen.mp3 ^
  --hidden-import=mutagen.flac ^
  --hidden-import=mutagen.mp4 ^
  --hidden-import=mutagen.oggvorbis ^
  --add-data "assets;assets" ^
  app.py
if errorlevel 1 goto :failed

if not exist "dist\Velora\Velora.exe" (
  echo ERROR: PyInstaller finished but Velora.exe was not found.
  goto :failed
)

echo.
echo BUILD SUCCESSFUL
echo Executable: %CD%\dist\Velora\Velora.exe
echo Distribute the complete dist\Velora folder, not only the EXE.
echo User settings and database are stored under %%LOCALAPPDATA%%\Velora.
if exist "dist\Velora_Portable_Windows.zip" del /q "dist\Velora_Portable_Windows.zip"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'dist\Velora\*' -DestinationPath 'dist\Velora_Portable_Windows.zip' -Force"
if errorlevel 1 (
  echo WARNING: App built, but ZIP packaging failed. Distribute the full dist\Velora folder.
) else (
  echo Portable package: %CD%\dist\Velora_Portable_Windows.zip
)
pause
exit /b 0

:failed
echo.
echo BUILD FAILED. Review the error above; the release was not created.
pause
exit /b 1
