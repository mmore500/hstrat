#!/bin/bash

# cd to script directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

echo "generating requirements-all.txt"
python3 -m uv pip compile --python-version=3.8 ../../pyproject.toml --extra pinned_dependencies_py38 --extra pinned_jit --extra docs --extra release --extra testing_py38 -o requirements-all.txt

echo "generating requirements-docs.txt"
python3 -m uv pip compile --python-version=3.8 ../../pyproject.toml --extra pinned_dependencies_py38 --extra docs -o requirements-docs.txt

echo "generating requirements-jit.txt"
python3 -m uv pip compile --python-version=3.8 ../../pyproject.toml --extra pinned_dependencies_py38 --extra pinned_jit -o requirements-jit.txt

echo "generating requirements-minimal.txt"
python3 -m uv pip compile --python-version=3.8 ../../pyproject.toml --extra pinned_dependencies_py38 -o requirements-minimal.txt

echo "generating requirements-release.txt"
python3 -m uv pip compile --python-version=3.8 --allow-unsafe ../../pyproject.toml --extra pinned_dependencies_py38 --extra release -o requirements-release.txt

echo "generating requirements-testing.txt"
python3 -m uv pip compile --python-version=3.8 ../../pyproject.toml --extra pinned_dependencies_py38 --extra pinned_jit --extra testing_py38 -o requirements-testing.txt
