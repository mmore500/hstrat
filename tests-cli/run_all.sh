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
for test in *.py; do
  echo "running test ${test}..."
  if python3 "${test}"; then
    echo "... ok!"
  else
    EXIT_CODE=1
    echo "... fail!"
  fi
done
fi

GLOBIGNORE="$(basename "$0")";
for test in *.sh; do
  echo "running test ${test}..."
  if bash "${test}"; then
    echo "... ok!"
  else
    EXIT_CODE=1
    echo "... fail!"
  fi
done

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "RUN ALL SUCCESS $0"
else
    echo "RUN ALL FAIL $0"
fi

exit ${EXIT_CODE}
