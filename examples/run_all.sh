#!/bin/bash

set -e

# cd to script directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

# adapted from https://unix.stackexchange.com/a/556639
GLOBIGNORE='_*';
for example in *.py; do
  echo "running example ${example}"
  python3 "${example}"
done

GLOBIGNORE="$(basename "$0")";
for example in *.sh; do
  echo "running example ${example}"
  bash "${example}"
done
