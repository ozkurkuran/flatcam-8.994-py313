#!/bin/sh -e
# Requires Python 3.13, its venv module, and matching Tcl/Tk support.
cd "$(dirname "$0")"
sudo apt-get install -y libgl1 libegl1 libglu1-mesa libxkbcommon-x11-0 libxcb-cursor0
python3.13 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
