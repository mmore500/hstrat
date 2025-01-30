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
