#!/bin/bash

# cd to scrip directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

./py37/regenerate.sh
# ./py38/regenerate.sh
# ./py39/regenerate.sh
./py310/regenerate.sh
# ./py311/regenerate.sh

for f in py37/*.txt; do
  cat "${f}" | sed "s/==/>=/g" > "$(basename "${f}")"
done
