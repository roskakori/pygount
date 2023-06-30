#!/bin/sh
set -e
poetry run pytest --cov-reset --cov=pygount --cov-branch --cov-report html
echo "To view results run: firefox htmlcov/index.html &"
