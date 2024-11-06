#!/bin/bash

set -e

cd "$(dirname "$0")/.."

tmpdir="$(mktemp -d)"
trap 'rm -rf -- "${tmpdir}"' EXIT
python3 -m venv "${tmpdir}"

source "${tmpdir}/bin/activate"
python3 -m pip install uv wheel
python3 -m uv pip install .

python3 ./tidy/impl/test_type_stubs_up_to_date.py
