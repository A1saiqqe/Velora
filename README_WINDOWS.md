# Velora — Windows 10/11

Velora is a Python desktop music player targeting Windows 10 and Windows 11 (64-bit).

## Run from source

If Python and the project dependencies are already installed on your computer, you do not need to create a new virtual environment just to run Velora.

1. Extract the project to a writable folder, for example `%USERPROFILE%\Projects\Velora`.
2. Open Command Prompt in that folder.
3. Run:

   ```bat
   python --version
   python -m compileall -q .
   python -m unittest discover -s tests -v
   python app.py
   ```

Run these commands using the same Python installation where `customtkinter`, `pygame`/`pygame-ce`, `Pillow`, and `mutagen` are installed. If the app reports a missing module, install that dependency into this interpreter.

## Build the Windows executable

Use a 64-bit Windows 10/11 machine. The build script prefers Python 3.12, then 3.11. Python 3.14 is selected only if the Python Launcher can find it; dependency installation and the test run must also succeed before packaging. From the extracted project folder, double-click `build_windows.bat` or run it from Command Prompt. The script creates a virtual environment, installs `requirements-build.txt`, runs the unit tests, and then builds the app with PyInstaller. If a dependency has no compatible wheel for your interpreter, use a supported interpreter listed in the script or update the dependency to a verified compatible release.

The executable is created at `dist\Velora\Velora.exe`, and the script also creates `dist\Velora_Portable_Windows.zip`. **Give end users the ZIP**: they extract it and run `Velora.exe`; they do not need Python. Do not distribute only the EXE, because the other files contain bundled runtime libraries. The build script intentionally fails if tests fail or the executable is missing.

To run the tests separately, use `run_tests.bat`, or run `python -m unittest discover -s tests -v` in the project folder.

## Data and privacy

The app stores its configuration, SQLite library database, and artwork cache in the current user's local application data directory (`%LOCALAPPDATA%\Velora`). This avoids writing into `Program Files` and avoids modifying the bundled application directory. In a packaged build, the initial music folder is the user's `Music` folder when available. Choose another folder in Settings to scan a different collection.

The home dashboard includes a large now-playing area, recently played/library cards, queue thumbnails, a current-track/favorites panel, and a dark purple-accent theme. The sidebar includes library, playlists, albums, artists, genres, folders, favorites, and settings. Search opens the library and filters by title, artist, or album. Album/artist/genre/folder/playlist play actions queue that collection rather than the full library.

The library database stores file paths and metadata; audio files are not copied into the database. The app scans supported formats including MP3, FLAC, WAV, OGG/OGA, M4A, OPUS, WMA, and AIFF. Actual codec support depends on the installed pygame/SDL_mixer build.

## Troubleshooting

- **No sound / mixer initialization error:** check the Windows output device, volume mixer, and whether audio is available in the current Remote Desktop session.
- **A track will not open:** the codec may not be supported by the installed SDL_mixer build, or the file may be damaged. Try MP3, WAV, or OGG.
- **A test fails:** save the full traceback and run the command from the same Python environment used to start the app.

## Python version note

The source code uses standard Python features and compiles under Python 3.13 in the development validation environment. The target interpreter is selected by `build_windows.bat`; the complete release still requires a successful dependency install, test run, and Windows smoke test on the selected interpreter. Do not treat source compilation alone as proof of Python 3.14 or Windows runtime compatibility.

## Validation status

Automated tests cover queue behavior (including shuffle cycles), SQLite repositories/playlists, configuration, and missing music folders. Run `python -m unittest discover -s tests -v`. GUI rendering and actual sound output still need to be tested on a Windows 10/11 computer. The executable must be built and smoke-tested on Windows; a source compile or Linux test run cannot verify Windows audio devices, GUI rendering, or the final package.
