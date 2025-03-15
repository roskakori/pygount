#!/bin/sh
# Build documentation using Sphinx
set -e
echo "🌱 Installing documentation dependencies"
uv sync --group docs
echo "📖 Building documentation"
make -C docs html
echo "🎉 Successfully built documentation in docs/_build/html/index.html"
