#!/bin/sh
# Build documentation using Sphinx of the poetry environment
#
# NOTE: Ideally we would use a virtual environment based on
# docs/requirements.txt. However, this environment also would the pygount
# module for Sphinx to find, which is not easy as this is managed by
# poetry instead of virtualenv.
#
# So for now, the local and CI build use the Sphinx from the poetry
# environment while the ReadTheDocs build uses virtualenv with some magic to
# find the pygount packages.
#
# As long as both the pyproject.toml and the docs/requirements.txt use the
# same version number, this should consistently detect possible errors in
# the build.
set -e
echo "🌱 Installing documentation dependencies"
poetry install --with docs
echo "📖 Building documentation"
make -C docs html
echo "🎉 Successfully built documentation in docs/_build/html/index.html"
