#!/bin/sh
set -e
echo "📖 Building documentation"
make -C docs html
echo "🎉 Successfully built documentation in docs/_build/html/index.html"
