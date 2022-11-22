#!/bin/bash

# cd to scrip directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

echo "generating requirements-all.txt"
python3.7 -m piptools compile ../pyproject.toml --extra pinned_dependencies --extra docs --extra release --extra testing -o requirements-all.txt

echo "generating requirements-docs.txt"
python3.7 -m piptools compile ../pyproject.toml --extra pinned_dependencies --extra docs -o requirements-docs.txt

echo "generating requirements-minimal.txt"
python3.7 -m piptools compile ../pyproject.toml --extra pinned_dependencies -o requirements-minimal.txt

echo "generating requirements-release.txt"
python3.7 -m piptools compile ../pyproject.toml --extra pinned_dependencies --extra release -o requirements-release.txt

echo "generating requirements-testing.txt"
python3.7 -m piptools compile ../pyproject.toml --extra pinned_dependencies --extra testing -o requirements-testing.txt
