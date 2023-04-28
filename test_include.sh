#!/bin/bash

set -e
shopt -s globstar

for f in include/**/*.hpp; do
  echo "${f}"
  printf "#include \"${f}\"\nint main(){}" | $CXX -std=c++20 $(python3 -m pybind11 --includes) -x c++ - -std=c++20 -DFMT_HEADER_ONLY -shared -fPIC -o /dev/null &

  # adapted from https://unix.stackexchange.com/a/436713
  if [[ $(jobs -r -p | wc -l) -ge 2 ]]; then
      # now there are $N jobs already running, so wait here for any job
      # to be finished so there is a place to start next one.
      wait -n
  fi
done
