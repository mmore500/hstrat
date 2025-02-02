#!/bin/bash

set -euo pipefail

# get example genome data
wget -O /tmp/hstrat-examples-genomes.pqt https://osf.io/gnkbc/download

# unpack and reconstruct, only first 100_000 genomes for this example
ls -1 /tmp/hstrat-examples-genomes.pqt \
    | python3 -O -m hstrat.dataframe.surface_build_tree \
        --head 100_000 \
        /tmp/reconstructed.csv

# convert from alifestd to newick
python3 -O -m hstrat._auxiliary_lib._alifestd_as_newick_asexual \
    -i /tmp/reconstructed.csv \
    -o /tmp/reconstructed.newick
