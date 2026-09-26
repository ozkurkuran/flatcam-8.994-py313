# FlatCAM beta 8.994

PCB CAM software by Marius Stanciu, based on FlatCAM by Juan Pablo Caram.
This tree is based on the [8.994 source archive](https://github.com/sasodoma/flatcam-archive/blob/main/FlatCAM_beta_8.994_sources.zip), dated 2020-11-07, with compatibility updates for Python 3.13, PyQt6, NumPy 2, Shapely 2, and current VisPy/Matplotlib.

## Windows setup (PowerShell)

Install 64-bit Python 3.13 with Tcl/Tk support, then run from this directory:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\run-flatcam.ps1
```

For a console with diagnostic messages:

```powershell
.\.venv\Scripts\python.exe FlatCAM.py
```

The tested Python patch version is recorded in `.python-version`. Runtime dependencies are pinned in `requirements.txt`. Rasterio wheels supply their own GDAL runtime; FlatCAM does not import `osgeo`. Qt 6 handles high-DPI scaling automatically. VisPy uses the PyQt6 backend and its current built-in rendering support.

## Checks

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tests/smoke_app.py
```

The smoke check opens a temporary application window with isolated settings, loads the bundled Gerber and Excellon examples, generates isolation geometry and G-code, saves/reloads a project, and captures `.venv/startup-smoke.png`. It requires a working desktop/OpenGL context. These checks cover the basic workflow; they do not exercise every editor, tool, machine, or postprocessor.

## Linux

Use Python 3.13 with its matching venv and Tcl/Tk packages, plus the system OpenGL/GLU and Qt xcb runtime libraries. `setup_ubuntu.sh` installs the runtime libraries and creates a local environment using `python3.13`. Linux has not been validated in this Windows workspace.

## Source and license

Original documentation: <http://flatcam.org/manual/index.html>.
The application remains version 8.994; these are dependency compatibility changes, not a new upstream release. See `LICENSE` and `CHANGELOG.md` for the original license and release history.
