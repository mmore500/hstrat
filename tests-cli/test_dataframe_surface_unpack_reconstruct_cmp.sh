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

echo "BEGIN $0"
echo "/ HSTRAT_TESTS_CLI_STDOUT=${HSTRAT_TESTS_CLI_STDOUT}"
echo "/ HSTRAT_TESTS_CLI_HEAD=${HSTRAT_TESTS_CLI_HEAD:-}"
EXIT_CODE=0

opts=(
    "--collapse-unif-freq=0" # opt1
    "--collapse-unif-freq=0" # opt2

    "--exploded-slice-size=4_000_000" # opt1
    "--exploded-slice-size=4_000_000" # opt2

    "--exploded-slice-size=4_000_000 --collapse-unif-freq=0" # opt1
    "--exploded-slice-size=1_000 --collapse-unif-freq=0" # opt2
)
for (( i=0; i<${#opts[@]} ; i+=2 )); do
    opt1="${opts[i]}"
    opt2="${opts[i+1]}"
    echo "   - opt1=${opt1} opt2=${opt2}"

    # unpack and reconstruct reference
    ls -1 "${genomes}" \
        | python3 -m hstrat.dataframe.surface_unpack_reconstruct "${reference}" \
        ${HSTRAT_TESTS_CLI_HEAD:-} ${opt1} \
        > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1

    # unpack and reconstruct alternate
    ls -1 "${genomes}" \
        | python3 -m hstrat.dataframe.surface_unpack_reconstruct "${alternate}" \
        ${HSTRAT_TESTS_CLI_HEAD:-} ${opt2} \
        > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1

    if cmp "${reference}" "${alternate}"; then
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
