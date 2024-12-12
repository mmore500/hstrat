#!/bin/bash

# cd to script directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

# python version 3.9 is symlinked to 3.8
./py310/regenerate.sh &

./py311/regenerate.sh &

./py312/regenerate.sh &

wait
