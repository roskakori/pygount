#!/bin/sh
# Update requirements files and pre-commit hooks to current versions.
set -e
echo "🧱 Updating project"
uv sync
uv lock --upgrade
echo "🛠️ Updating pre-commit"
pre-commit autoupdate
echo "📖 Updating documentation"
pur -r docs/requirements.txt
echo "🎉 Successfully updated dependencies"
