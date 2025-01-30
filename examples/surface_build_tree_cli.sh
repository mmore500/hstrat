#!/bin/bash

set -euo pipefail

wget -O /tmp/genomes.pqt https://osf.io/gnkbc/download

ls -1 /tmp/genomes.pqt \
    | python3 -O -m hstrat.dataframe.surface_build_tree /tmp/reconstructed.csv

python3 -O -m hstrat._auxiliary_lib._alifestd_as_newick_asexual \
    -i /tmp/reconstructed.csv \
    -o /tmp/reconstructed.newick
