#!/bin/bash

set -euo pipefail   # stop running if something errs (ex. a KB interrupt)

if [[ $# -ne 2 ]]; then
  echo "Must pass in a two arguments, the first denoting the maximum number of jobs running at a time and the second denoting the number of samples"
  exit
fi

echo "which python3 $(which python3)"
python3 --version
python3 -m pip show downstream
python3 examples/end2end_tree_reconstruction_test.py --help | head -20
python3 examples/end2end_tree_reconstruction_test.py --help  | head -20 &
wait

for i in $(seq 1 $2); do
  while [[ $(jobs | wc -l) -ge $1 ]]; do
    sleep 1
  done
  echo "Spawning job $i"
  echo python3 examples/end2end_tree_reconstruction_test.py \
    --skip-vis \
    --no-preset-random \
    --repeats 1 \
    --fossil-interval None 200 50 \
    --reconstruction-algo shortcut naive \
    --retention-algo dstream.hybrid_0_steady_1_tilted_2_algo \
    --differentia-bitwidth 64 8 1 \
    --surface-size 256 32 16 \
    --output-path "end2end-reconstruction-error-$i.csv"
  python3 examples/end2end_tree_reconstruction_test.py \
    --skip-vis \
    --no-preset-random \
    --repeats 1 \
    --fossil-interval None 200 50 \
    --reconstruction-algo shortcut naive \
    --retention-algo dstream.steady_algo dstream.tilted_algo dstream.stretched_algo dstream.hybrid_0_steady_1_tiltedxtc_2_algo \
    --differentia-bitwidth 64 8 1 \
    --surface-size 256 32 16 \
    --output-path end2end-reconstruction-error-$i.csv \
    2>&1 | tee "run-$i.log" &
done

wait

zip data.zip end2end-reconstruction-error-*.csv
zip archive.zip run-*.log
