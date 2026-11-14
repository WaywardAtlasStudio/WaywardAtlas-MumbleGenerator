# Wayward Atlas Mumble Generator

**Version:** 1.0.0  
**Developer:** Wayward Atlas Studio  
**Copyright:** © 2026 Wayward Atlas Studio

## About

Wayward Atlas Mumble Generator creates original, synthetic character-voice samples for games and other creative projects.

### Features

- Graphical user interface and command-line audio engine
- Four presets: Neutral, Tiny Creature, Deep Voice, and Robot
- Adjustable pitch, duration, and volume
- Six generated WAV samples per voice pack
- Speech-preview WAV
- ZIP export with included README


## Requirements

The following dependency versions were used in our tested development environments.

**Linux:**
- Python 3.13
- NumPy 2.2.4
- SciPy 1.15.3

**Windows:**
- Python 3.15
- NumPy 2.5.4
- SciPy 1.18.1

PyInstaller 6.22.3 was used for standalone executable builds.

Compatibility with other Python or dependency versions is not guaranteed.

### Installing Dependencies

Create and activate a Python virtual environment before installing dependencies.

**Linux (Python 3.13):**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If your system's `python3` command already uses Python 3.13, you may use `python3 -m venv .venv` instead.

**Windows (Python 3.15):**

```powershell
py -3.15 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-windows.txt
```

Run these commands from the source project's root directory.

Activate the same virtual environment again whenever you return to the project.

## Running From Source

After installing the appropriate dependencies, launch the graphical interface:

```bash
python generator/mumble_gui.py
```

Or use the command-line generator:

```bash
python generator/make_mumble_pack.py --preset robot
```

Available voice presets and command-line options are defined by the generator.

Generated audio packs are written to the output directory.

## Building Standalone Applications

### Install Build Dependencies

Activate the virtual environment created earlier, then install the build requirements for your operating system.

**Linux (Python 3.13):**

```bash
python -m pip install -r requirements-build.txt
```

**Windows (Python 3.15):**

```powershell
python -m pip install -r requirements-build-windows.txt
```

Both tested environments use PyInstaller 6.22.3.

Build executables on their target operating systems. PyInstaller does not directly cross-compile Windows and Linux applications.

### Building the GUI

The GUI uses a directory-based PyInstaller build.

```bash
python -m PyInstaller --onedir --windowed --name WaywardAtlas_MumbleGenerator generator/mumble_gui.py
```

The resulting application directory is created under `dist/`.

### Building the Audio Engine

The audio engine uses different packaging configurations on Linux and Windows.

**Linux audio engine (Python 3.13):**

```bash
python -m PyInstaller --onedir --console \
  --contents-directory _engine_internal \
  --exclude-module readline \
  --exclude-module rlcompleter \
  --name WaywardAtlas_MumbleEngine \
  generator/make_mumble_pack.py
```

This produces a directory containing the engine executable and its `_engine_internal` dependency directory.

**Windows audio engine (Python 3.15):**

```powershell
python -m PyInstaller --onefile --console --name WaywardAtlas_MumbleEngine generator/make_mumble_pack.py
```

This produces a standalone engine executable.

### Preparing a Distribution

The GUI and audio engine must both be included.

For Windows, place the generated engine executable alongside the GUI executable inside the GUI application's distribution directory.

For Linux, place the engine executable and its `_engine_internal` directory alongside the GUI executable and its `_internal` directory inside the final application directory.

Include any required application assets, documentation, license files, third-party notices, and other runtime files.

Linux builds may also require compatible system-installed shared libraries.

These commands provide a starting point for developers building from source. They are not a complete, reproducible procedure for creating the official Wayward Atlas Studio release archives. Additional runtime-library configuration, packaging, and licensing requirements may apply.


## Licensing

See the following files:

- `LICENSE` — application license
- `NOTICE` — copyright information
- `GENERATED_AUDIO_LICENSE.txt` — generated audio licensing
- `THIRD_PARTY_LICENSES/` — third-party notices and licenses

Bundled binary dependencies may require additional redistribution conditions, including corresponding-source access or library-replacement provisions.

## Project

Wayward Atlas Studio