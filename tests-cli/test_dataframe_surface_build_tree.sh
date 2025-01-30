#!/bin/bash

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

HSTRAT_TESTS_CLI_STDOUT="${HSTRAT_TESTS_CLI_STDOUT:-/dev/null}"

genomes="$(mktemp).pqt"
reference="$(mktemp).pqt"
alternate="$(mktemp).pqt"

# get example genome data
wget -O "${genomes}" https://osf.io/gnkbc/download \
    > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1

# unpack and reconstruct reference
ls -1 "${genomes}" \
    | python3 -O -m hstrat.dataframe.surface_build_tree "${reference}" \
    > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1 &


# unpack and reconstruct alternate
ls -1 "${genomes}" \
    | python3 -O -m hstrat.dataframe.surface_build_tree "${alternate}" \
    > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1 &

wait

cmp "${reference}" "${alternate}"  \
    && echo "PASS $0" \
    || echo "FAIL: $0" && exit 1
