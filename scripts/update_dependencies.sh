#!/bin/sh
# Update requirements files and pre-commit hooks to current versions.
set -e
echo "🧱 Updating project"
uv sync
uv lock --upgrade
echo "🛠️ Updating pre-commit"
uv run pre-commit autoupdate
echo "📖 Updating documentation"
# HACK This is only needed because ReadTheDocs cannot extract the
#  dependencies from pyproject.toml.
uv export --no-hashes --format requirements-txt > docs/requirements.txt
echo "🎉 Successfully updated dependencies"
