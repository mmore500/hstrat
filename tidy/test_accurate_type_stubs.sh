#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python3.11 -m venv .temp
source .temp/bin/activate
python3.11 -m pip install uv wheel
python -m uv pip install .
python3 ./tidy/impl/test_accurate_type_stubs.py
deactivate
rm -rf .temp
