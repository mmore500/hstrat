#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

python3 ./_test_reconstruct.py

echo "$0 All tests passed!"
