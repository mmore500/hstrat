#!/bin/bash

# cd to script directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

# python version 3.9 is symlinked to 3.8
./py38/regenerate.sh &

./py310/regenerate.sh &

./py311/regenerate.sh &

wait

for f in py38/*.txt; do
  cat "${f}" \
    | sed "s/==/>=/g" \
    | sed "s/numpy>=/numpy<2,>=/g" \
    | sed "s/pandas>=/pandas<2,>=/g" \
    > "$(basename "${f}")"
done
