# Velora Music Player — release preparation

## Included in this project

- Dark desktop interface with purple accent styling and Manrope fonts.
- Local audio library scanning and metadata extraction.
- Playback controls, seeking, volume, shuffle, repeat, and queue management.
- SQLite-backed favorites and playlists.
- Library, favorites, albums, artists, genres, folders, playlists, and settings pages.
- Per-user writable data under `%LOCALAPPDATA%\Velora` on Windows.
- Windows build script that runs automated tests before invoking PyInstaller.

## Build a Windows release

On a 64-bit Windows 10/11 machine, install Python 3.11 or 3.12 and run `build_windows.bat`.
The script creates/uses `.venv`, installs dependencies, runs tests, and builds `dist\Velora\Velora.exe`.
Distribute the entire `dist\Velora` directory because it contains required runtime libraries.

## Validation notes

The source tree compiles and the included automated unit tests can be run with:

```bat
python -m compileall -q .
python -m unittest discover -s tests -v
```

A Windows executable must be built and smoke-tested on Windows. A Linux-side source audit does not establish that Windows audio devices, codecs, rendering, or packaging work on every target machine.
