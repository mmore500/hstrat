#!/bin/bash

set -e

# cd to scrip directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

# adapted from https://unix.stackexchange.com/a/556639
GLOBIGNORE='_*';
for example in *.py; do
  python3 "${example}"
done
