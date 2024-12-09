#!/bin/bash

set -e

shopt -s nullglob

cd "$(dirname "$0")"

cmake .
make

for object in *.so; do
    filename="${object%%.*}"
    sourcename="$(find hstrat -name "${filename}.cpp" -type f)"
    where="$(dirname "${sourcename}")"
    echo "Copying ${object} to ${where}"
    cp "${object}" "${where}"
done
