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
cp /tmp/hstrat-gnkbc.pqt "${genomes}" 2>/dev/null \
    || { wget -O "${genomes}" https://osf.io/gnkbc/download \
    > "${HSTRAT_TESTS_CLI_STDOUT}" 2>&1 \
    && cp "${genomes}" /tmp/hstrat-gnkbc.pqt; }

echo "BEGIN $0"
echo "/ HSTRAT_TESTS_CLI_STDOUT=${HSTRAT_TESTS_CLI_STDOUT}"
echo "/ HSTRAT_TESTS_CLI_HEAD=${HSTRAT_TESTS_CLI_HEAD:-}"
EXIT_CODE=0

for opt in \
    "--check-trie-invariant-freq=1" \
    "--check-trie-invariant-freq=1 --collapse-unif-freq=1 --check-trie-invariant-after-collapse-unif" \
; do
    echo "   - opt=${opt}"

    # unpack and reconstruct alternate
    # shellcheck disable=SC2086  # intentional word splitting
    if ls -1 "${genomes}" \
        | python3 -m hstrat.dataframe.surface_build_tree "${alternate}" \
        ${HSTRAT_TESTS_CLI_HEAD:-} ${opt} \
        > "${HSTRAT_TESTS_CLI_STDOUT}" 2>&1 \
    ; then
        echo "   + PASS"
    else
        EXIT_CODE=1
        echo "   x FAIL"
    fi

done

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "SUCCESS $0"
else
    echo "FAIL $0"
fi

exit ${EXIT_CODE}
