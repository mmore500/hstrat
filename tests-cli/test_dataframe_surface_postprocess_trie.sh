#!/bin/bash

set -euo pipefail

HSTRAT_TESTS_CLI_STDOUT="${HSTRAT_TESTS_CLI_STDOUT:-/dev/null}"

genomes="$(mktemp).pqt"
trie="$(mktemp).pqt"
reference="$(mktemp).pqt"
alternate="$(mktemp).pqt"

# get example genome data
wget -O "${genomes}" https://osf.io/gnkbc/download \
    >${HSTRAT_TESTS_CLI_STDOUT} 2>&1

# unpack and reconstruct
ls -1 "${genomes}" \
    | python3 -O -m hstrat.dataframe.surface_build_tree "${trie}" \
    >${HSTRAT_TESTS_CLI_STDOUT}

# postproccess reference
ls -1 "${trie}" \
    | python3 -O -m hstrat.dataframe.surface_postprocess_trie "${reference}" \
    >${HSTRAT_TESTS_CLI_STDOUT} &

# postprocess alternate
ls -1 "${trie}" \
    | python3 -O -m hstrat.dataframe.surface_postprocess_trie "${alternate}" \
    >${HSTRAT_TESTS_CLI_STDOUT} &

wait

cmp "${reference}" "${alternate}"  \
    && echo "PASS $0" \
    || echo "FAIL: $0" && exit 1
