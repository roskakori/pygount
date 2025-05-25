#!/bin/sh
# Build documentation using Sphinx
set -e
echo "📖 Building documentation"
mkdocs build
echo "✅ Successfully built documentation in site/index.html"
