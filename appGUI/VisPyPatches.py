"""Select the Qt backend using VisPy's public API.

VisPy 0.17 handles grid layout, infinite lines and tick labels itself. The
legacy private-API patches are no longer needed or compatible with it.
"""
from vispy import app


def apply_patches():
    app.use_app('pyqt6')
