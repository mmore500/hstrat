#!/bin/bash

set -e

# cd to script directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

EXIT_CODE=0

# adapted from https://unix.stackexchange.com/a/556639
GLOBIGNORE='_*';
# adapted from https://stackoverflow.com/a/34195247/17332200
if compgen -G "*.py"; then
for example in *.py; do
  echo "running example ${example}"
  python3 "${example}" || EXIT_CODE=1
done
fi

GLOBIGNORE="$(basename "$0")";
for example in *.sh; do
  echo "running example ${example}"
  bash "${example}" || EXIT_CODE=1
done

echo "exiting with exit code ${EXIT_CODE}"
exit ${EXIT_CODE}
