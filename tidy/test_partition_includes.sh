#!/bin/bash
set -e

# enforce use of GNU version of coreutils
. ./tidy/util/enforce_gnu_utils.sh

# refuse to continue if uncommitted changes are present
. ./tidy/util/enforce_git_status.sh

SOURCE_HASH=$( find -path ./third-party -prune -false -o -type f | sort | xargs cat | sha1sum )

./tidy/impl/partition_includes.sh

if [ "${SOURCE_HASH}" == "$( find -path ./third-party -prune -false -o -type f | sort | xargs cat | sha1sum )" ];
then
  exit 0 # success
else
  echo "unpartitioned includes detected, run ./tidy/impl/partition_includes.sh locally to find & fix"
  exit 1 # failure
fi
