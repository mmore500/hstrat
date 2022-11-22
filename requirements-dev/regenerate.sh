#!/bin/bash

# cd to scrip directory
# adapted from https://stackoverflow.com/a/6393573
cd "${0%/*}"

./py37/regenerate.sh
./py310/regenerate.sh
