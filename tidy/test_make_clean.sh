#!/bin/bash
set -e

# enforce use of GNU version of coreutils
. ./tidy/util/enforce_gnu_utils.sh

# enforce availability of dependencies
. ./tidy/util/enforce_dependency.sh sphinx-build

SOURCE_HASH=$( find -path ./third-party -prune -false -o -type f | sort | xargs cat | sha1sum )

make -C docs clean

if [ "${SOURCE_HASH}" == "$( find -path ./third-party -prune -false -o -type f | sort | xargs cat | sha1sum )" ];
then
  exit 0 # success
else
  echo "compilation artifacts detected, run make clean locally to find & fix"
  exit 1 # failure
fi
