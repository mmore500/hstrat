#!/bin/bash

# cd to script directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

# python version 3.9 is symlinked to 3.8
./py38/regenerate.sh

./py310/regenerate.sh

./py311/regenerate.sh

for f in py38/*.txt; do
  cat "${f}" | sed "s/==/>=/g" > "$(basename "${f}")"
done
