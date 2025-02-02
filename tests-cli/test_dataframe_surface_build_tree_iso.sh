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

# unpack and reconstruct reference
ls -1 "${genomes}" \
    | python3 -m hstrat.dataframe.surface_build_tree "${reference}" \
    ${HSTRAT_TESTS_CLI_HEAD:-} --collapse-unif-freq=0 \
    > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1

echo "BEGIN $0"
echo "/ HSTRAT_TESTS_CLI_STDOUT=${HSTRAT_TESTS_CLI_STDOUT}"
echo "/ HSTRAT_TESTS_CLI_HEAD=${HSTRAT_TESTS_CLI_HEAD:-}"
EXIT_CODE=0

echo "      ! info: reference num root nodes $( \
    python3 -m hstrat._auxiliary_lib._alifestd_count_root_nodes \
    "${reference}" \
)"

for opt in \
    "--collapse-unif-freq=-1" \
    "--exploded-slice-size=4_000_000 --collapse-unif-freq=0" \
    "--exploded-slice-size=1_000 --collapse-unif-freq=0" \
    "" \
    "--exploded-slice-size=1_000_000" \
    "--exploded-slice-size=4_000_000" \
; do
    echo "   - opt=${opt}"

    # unpack and reconstruct alternate
    ls -1 "${genomes}" \
        | python3 -m hstrat.dataframe.surface_build_tree "${alternate}" \
        ${HSTRAT_TESTS_CLI_HEAD:-} ${opt} \
        > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1

    echo "      ! info: alternate num root nodes $( \
        python3 -m hstrat._auxiliary_lib._alifestd_count_root_nodes \
        "${alternate}" \
    )"

    if python3 \
        -m hstrat._auxiliary_lib._alifestd_test_leaves_isomorphic_asexual \
        --taxon-label "dstream_data_id" \
        "${reference}" "${alternate}" \
        > ${HSTRAT_TESTS_CLI_STDOUT} 2>&1 \
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
