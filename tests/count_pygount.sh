#!/usr/bin/env bash
# Install pygount in a new environment and count its lines of code.
set -ex
python3 -m venv tests/.temp/env_count
source tests/.temp/env_count/bin/activate
pip3 install --upgrade pip
pip3 install --requirement dev-requirements.txt

python3 setup.py install
tests/.temp/env_count/bin/pygount --format=cloc-xml --out cloc.xml --verbose build.xml pygount setup.py tests

deactivate
