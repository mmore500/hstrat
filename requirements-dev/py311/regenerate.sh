#!/bin/bash

# cd to script directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

echo "generating requirements-all.txt"
python3 -m uv pip compile --python-version=3.11 ../../pyproject.toml --extra docs --extra release --extra testing --extra jit -o requirements-all.txt

echo "generating requirements-docs.txt"
python3 -m uv pip compile --python-version=3.11 ../../pyproject.toml --extra docs -o requirements-docs.txt

echo "generating requirements-jit.txt"
python3 -m uv pip compile --python-version=3.11 ../../pyproject.toml --extra jit -o requirements-jit.txt

echo "generating requirements-minimal.txt"
python3 -m uv pip compile --python-version=3.11 ../../pyproject.toml -o requirements-minimal.txt

echo "generating requirements-release.txt"
python3 -m uv pip compile --python-version=3.11  --allow-unsafe ../../pyproject.toml --extra release -o requirements-release.txt

echo "generating requirements-testing.txt"
python3 -m uv pip compile --python-version=3.11 ../../pyproject.toml --extra testing --extra jit -o requirements-testing.txt
