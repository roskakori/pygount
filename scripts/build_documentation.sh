#!/bin/sh
set -e
echo "🌱 Setting up environment to build documentation"
virtualenv .venv-sphinx
. .venv-sphinx/bin/activate
pip install -r docs/requirements.txt
echo "📖 Building documentation"
make -C docs html
echo "🎉 Successfully built documentation in docs/_build/html/index.html"
