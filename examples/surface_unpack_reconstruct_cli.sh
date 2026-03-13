#!/bin/bash

set -euo pipefail

# get example genome data
cp /tmp/hstrat-gnkbc.pqt /tmp/genomes.pqt 2>/dev/null \
    || { wget -O /tmp/genomes.pqt https://osf.io/gnkbc/download \
    && cp /tmp/genomes.pqt /tmp/hstrat-gnkbc.pqt; }

# unpack and reconstruct
# note: in most cases the surface_build_tree cli should be preferred,
# as it incorporates key postprocessing steps
ls -1 /tmp/genomes.pqt \
    | python3 -O -m hstrat.dataframe.surface_unpack_reconstruct \
     --exploded-slice-size 100000 \
     /tmp/reconstruct1.csv
