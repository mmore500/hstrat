#!/bin/bash

set -euo pipefail

# get example genome data
wget -O /tmp/genomes.pqt https://osf.io/gnkbc/download

# unpack and reconstruct
# note: in most cases the surface_build_tree cli should be preferred,
# as it incorporates key postprocessing steps
ls -1 /tmp/genomes.pqt \
    | python3 -O -m hstrat.dataframe.surface_unpack_reconstruct \
     /tmp/reconstruct1.csv

# optional perf-tuning args
ls -1 /tmp/genomes.pqt \
    | python3 -O -m hstrat.dataframe.surface_unpack_reconstruct \
        /tmp/reconstruct2.csv \
        --exploded-slice-size=100000

cmp /tmp/reconstruct1.csv /tmp/reconstruct2.csv  # should give same result
