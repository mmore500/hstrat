#!/bin/bash

set -euo pipefail   # stop running if something errs (ex. a KB interrupt)
trap "kill 0" EXIT  # kill background processes if script exits

if [[ $# -ne 2 ]]; then
  echo "Must pass in a two arguments, the first denoting the maximum number of jobs running at a time and the second denoting the number of samples"
  exit
fi

echo "which python3 $(which python3)"
python3 --version
python3 examples/end2end_tree_reconstruction_test.py --help
python3 examples/end2end_tree_reconstruction_test.py --help &
wait

for i in $(seq 1 $2); do
  while [[ $(jobs | wc -l) -ge $1 ]]; do
    sleep 1
  done
  echo "Spawning job $i"
  python3 examples/end2end_tree_reconstruction_test.py \
    --skip-vis \
    --no-preset-random \
    --repeats 1 \
    --fossil-interval None 200 50 \
    --reconstruction-algo shortcut naive \
    --retention-algo dstream.steady_algo dstream.tilted_algo dstream.stretched_algo \
    --differentia-bitwidth 64 8 1 \
    --surface-size 256 32 16 \
    --output-path end2end-reconstruction-error-$i.csv \
    2>&1 | tee "run-$i.log" &
done

wait

zip data.zip end2end-reconstruction-error-*.csv
zip archive.zip run-*.log
