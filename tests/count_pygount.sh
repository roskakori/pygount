#!/usr/bin/env bash
# Install pygount in a new environment and count its lines of code.
python3 -m venv tests/.temp/env_count
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi

source tests/.temp/env_count/bin/activate
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi

pip3 install -r dev-requirements.txt
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi

python3 setup.py install
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi

tests/.temp/env_count/bin/pygount --format=cloc-xml --out cloc.xml --verbose build.xml pygount setup.py tests
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi

