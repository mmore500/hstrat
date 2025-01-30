#!/bin/bash

set -euo pipefail

HSTRAT_TESTS_CLI_STDOUT="${HSTRAT_TESTS_CLI_STDOUT:-/dev/null}"

genomes="$(mktemp).pqt"
reference="$(mktemp).pqt"
alternate="$(mktemp).pqt"

# get example genome data
wget -O "${genomes}" https://osf.io/gnkbc/download \
    > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1

# unpack and reconstruct reference
ls -1 "${genomes}" \
    | python3 -O -m hstrat.dataframe.surface_unpack_reconstruct "${reference}" \
    > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1 &

# unpack and reconstruct alternate
ls -1 "${genomes}" \
    | python3 -O -m hstrat.dataframe.surface_unpack_reconstruct "${alternate}" \
    > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1 &

wait

cmp "${reference}" "${alternate}"  \
    && echo "PASS $0" \
    || echo "FAIL: $0" && exit 1
