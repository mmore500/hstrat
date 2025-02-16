#!/bin/bash
set -e

cd "$(dirname "$0")/.."

# enforce use of GNU version of coreutils
# (ensuring GNU utils at startup reduces redundant verbosity)
. ./tidy/util/enforce_gnu_utils.sh

echo "Running tidyness enforcement tests..."
echo "See https://empirical.readthedocs.io/en/latest/dev/guide-to-testing.html#tidyness-enforcement for info on tidyness enforcement."
echo "(Including how to automatically generate tidyness fixes if tidyness enforcement detects tidyness issues.)"

./tidy/test_alphabetize_includes.sh && echo "✔ include alphabetization ok" || exit 1
./tidy/test_partition_includes.sh && echo "✔ include partitioning ok" || exit 1
./tidy/test_boilerplate.sh && echo "✔ boilerplate ok" || exit 1
./tidy/test_merge_conflict_markers.sh && echo "✔ conflict markers ok" || exit 1
./tidy/test_end_of_file_newlines.sh && echo "✔ EOF newlines ok" || exit 1
./tidy/test_tabs.sh && echo "✔ no tabs, indentation ok" || exit 1
./tidy/test_2space_indentation.sh && echo "✔ 2-space indents, indentation ok" || exit 1
./tidy/test_trailing_whitespace.sh && echo "✔ trailing whitespace ok" || exit 1
./tidy/test_filename_whitespace.sh && echo "✔ filename whitespace ok" || exit 1
./tidy/test_modern_suffixes.sh && echo "✔ modern suffixes ok" || exit 1
./tidy/test_make_clean.sh && echo "✔ no compilation artifacts" || exit 1
./tidy/test_type_stubs_up_to_date.sh && echo "✔ type stubs up to date" || exit 1
./tidy/test_lint.sh && echo "✔ no lint violations" || exit 1
