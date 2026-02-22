#!/bin/bash

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

HSTRAT_TESTS_CLI_STDOUT="${HSTRAT_TESTS_CLI_STDOUT:-/dev/null}"

genomes="$(mktemp).pqt"
trie="$(mktemp).pqt"

function cleanup {
    rm -f "${genomes}"
    rm -f "${trie}"
}
trap cleanup EXIT

err() {
    echo "FAIL line $(caller)" >&2
}
trap err ERR

# get example genome data
cp /tmp/hstrat-gnkbc.pqt "${genomes}" 2>/dev/null \
    || { wget -O "${genomes}" https://osf.io/gnkbc/download \
    > "${HSTRAT_TESTS_CLI_STDOUT}" 2>&1 \
    && cp "${genomes}" /tmp/hstrat-gnkbc.pqt; }

echo "BEGIN $0"
echo "/ HSTRAT_TESTS_CLI_STDOUT=${HSTRAT_TESTS_CLI_STDOUT}"
echo "/ HSTRAT_TESTS_CLI_HEAD=${HSTRAT_TESTS_CLI_HEAD:-}"
EXIT_CODE=0

for opt in \
    "" \
    "--collapse-unif-freq=0" \
    "--exploded-slice-size=4_000_000" \
; do
    echo "   - begin opt=${opt}"

    # unpack and reconstruct, keeping dstream metadata for validation
    # shellcheck disable=SC2086
    ls -1 "${genomes}" \
        | python3 -m hstrat.dataframe.surface_unpack_reconstruct "${trie}" \
        ${HSTRAT_TESTS_CLI_HEAD:-} ${opt} --no-drop-dstream-metadata \
        > "${HSTRAT_TESTS_CLI_STDOUT}" 2>&1

    # validate trie
    if python3 -m hstrat.dataframe.surface_validate_trie "${trie}" \
        --max-num-checks 10_000 \
        > "${HSTRAT_TESTS_CLI_STDOUT}" 2>&1 \
    ; then
        echo "   + PASS"
    else
        echo "   x FAIL"
        EXIT_CODE=1
    fi

done

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "SUCCESS $0"
else
    echo "FAIL $0"
fi

exit ${EXIT_CODE}
