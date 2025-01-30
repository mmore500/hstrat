#!/bin/bash

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

HSTRAT_TESTS_CLI_STDOUT="${HSTRAT_TESTS_CLI_STDOUT:-/dev/null}"

genomes="$(mktemp).pqt"
reference="$(mktemp).pqt"
alternate="$(mktemp).pqt"

function cleanup {
    rm -f "${genomes}"
    rm -f "${reference}"
    rm -f "${alternate}"
}
trap cleanup EXIT

err() {
    echo "FAIL line $(caller)" >&2
}
trap err ERR

# get example genome data
wget -O "${genomes}" https://osf.io/gnkbc/download \
    > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1

while read -r opt1 opt2; do

    echo "opt1=${opt1} opt2=${opt2}"

    # unpack and reconstruct reference
    ls -1 "${genomes}" \
        | python3 -O -m hstrat.dataframe.surface_unpack_reconstruct "${reference}" \
        ${HSTRAT_TESTS_CLI_HEAD:-} ${opt1} \
        > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1

    # unpack and reconstruct alternate
    ls -1 "${genomes}" \
        | python3 -O -m hstrat.dataframe.surface_unpack_reconstruct "${alternate}" \
        ${HSTRAT_TESTS_CLI_HEAD:-} ${opt2} \
        > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1

    cmp "${reference}" "${alternate}"  \
        && echo "PASS $0"

done< <(
    echo \
    \
    "--exploded-slice-size=4_000_000 --collapse-unif-freq=0" \
        "--exploded-slice-size=1_000 --collapse-unif-freq=0" \
    "--collapse-unif-freq=0" "--collapse-unif-freq=0" \
    \
    "--exploded-slice-size=4_000_000" "--exploded-slice-size=4_000_000" \
    \
    | xargs -n2
)
