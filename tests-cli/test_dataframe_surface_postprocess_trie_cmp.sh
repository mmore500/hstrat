#!/bin/bash

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

HSTRAT_TESTS_CLI_STDOUT="${HSTRAT_TESTS_CLI_STDOUT:-/dev/null}"

genomes="$(mktemp).pqt"
trie="$(mktemp).pqt"
reference="$(mktemp).pqt"
alternate="$(mktemp).pqt"

function cleanup {
    rm -f "${genomes}"
    rm -f "${trie}"
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
    >${HSTRAT_TESTS_CLI_STDOUT} 2>&1

# unpack and reconstruct
ls -1 "${genomes}" \
    | python3 -O -m hstrat.dataframe.surface_unpack_reconstruct "${trie}" \
    ${HSTRAT_TESTS_CLI_HEAD:-} \
    >${HSTRAT_TESTS_CLI_STDOUT} 2>&1

rm -f "${genomes}"

echo "BEGIN $0"
echo "/ HSTRAT_TESTS_CLI_STDOUT=${HSTRAT_TESTS_CLI_STDOUT}"
echo "/ HSTRAT_TESTS_CLI_HEAD=${HSTRAT_TESTS_CLI_HEAD:-}"
EXIT_CODE=0

# postproccess reference
ls -1 "${trie}" \
    | python3 -m hstrat.dataframe.surface_postprocess_trie "${reference}" \
    >${HSTRAT_TESTS_CLI_STDOUT} 2>&1

# postprocess alternate
ls -1 "${trie}" \
    | python3 -m hstrat.dataframe.surface_postprocess_trie "${alternate}" \
    >${HSTRAT_TESTS_CLI_STDOUT} 2>&1

if cmp "${reference}" "${alternate}"; then
    echo "   + PASS"
else
    EXIT_CODE=1
    echo "   x FAIL"
fi

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "SUCCESS $0"
else
    echo "FAIL $0"
fi

exit ${EXIT_CODE}
