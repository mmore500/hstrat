#!/bin/bash

set -euo pipefail

has_cppimport="$(python3 -m pip freeze | grep '^cppimport==' | wc -l)"
if [ "${has_cppimport}" -eq 0 ]; then
    echo "cppimport required for $(basename "$0") but not installed." >&2
    echo "python3 -m pip install cppimport" >&2
    exit 1
fi

cd "$(dirname "$0")"

id="$(date +"%H-%M-%S")-$(uuidgen)"
genome_df_path="/tmp/end2end-raw-genome-evolve_surf_dstream_$id.pqt"
true_phylo_df_path="/tmp/end2end-true-phylo-evolve_surf_dstream_$id.csv"
reconst_phylo_df_path="/tmp/end2end-reconst-phylo-evolve_surf_dstream_$id.pqt"

# generate data
./evolve_dstream_surf.py \
    "$@" \
    --genome-df-path "${genome_df_path}" \
    --phylo-df-path "${true_phylo_df_path}" \
    >&2

# do reconstruction
ls "${genome_df_path}" | python3 -m \
    hstrat.dataframe.surface_unpack_reconstruct \
    "${reconst_phylo_df_path}" \
    --reconstruction-algorithm "${HSTRAT_RECONSTRUCTION_ALGO:-shortcut}" \
    >&2

# log output paths
echo "genome_df_path = '${genome_df_path}'"
echo "true_phylo_df_path = '${true_phylo_df_path}'"
echo "reconst_phylo_df_path = '${reconst_phylo_df_path}'"
