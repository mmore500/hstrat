#!/bin/bash

set -e

cd "$(dirname "$0")/.."

python3 -m black --check --diff .
python3 -m isort --check-only --diff .
