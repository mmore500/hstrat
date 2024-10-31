#!/bin/bash

set -e

cd "$(dirname "$0")/.."

python3 -m venv .temp
source .temp/bin/activate
python3 -m pip install uv wheel
python3 -m uv pip install .
python3 ./tidy/impl/test_accurate_type_stubs.py
deactivate
rm -rf .temp
