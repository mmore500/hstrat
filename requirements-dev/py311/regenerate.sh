#!/bin/bash

# cd to script directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

echo "generating requirements-all.txt"
python3.11 -m piptools compile ../../pyproject.toml --extra pinned_dependencies_py310 --extra docs --extra release --extra testing_py310 -o requirements-all.txt

echo "generating requirements-docs.txt"
python3.11 -m piptools compile ../../pyproject.toml --extra pinned_dependencies_py310 --extra docs -o requirements-docs.txt

echo "generating requirements-minimal.txt"
python3.11 -m piptools compile ../../pyproject.toml --extra pinned_dependencies_py310 -o requirements-minimal.txt

echo "generating requirements-release.txt"
python3.11 -m piptools compile  --allow-unsafe ../../pyproject.toml --extra pinned_dependencies_py310 --extra release -o requirements-release.txt

echo "generating requirements-testing.txt"
python3.11 -m piptools compile ../../pyproject.toml --extra pinned_dependencies_py310 --extra testing_py310 -o requirements-testing.txt
