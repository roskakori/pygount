#!/bin/sh
# Update requirements files and pre-commit hooks to current versions.
set -e
echo "🧱 Updating project"
uv sync
uv lock --upgrade
echo "🛠️ Updating pre-commit"
uv run pre-commit autoupdate
echo "🎉 Successfully updated dependencies"
