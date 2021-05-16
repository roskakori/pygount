#!/bin/sh
# Update requirements files and pre-commit hooks to current versions.
set -e
pip install --upgrade pip
pur -r dev-requirements.txt
pip install -r dev-requirements.txt
pre-commit autoupdate
