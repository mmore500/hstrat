#!/usr/bin/env python3

import gzip
import io
import json
import os
import tempfile

import yaml

from hstrat import hstrat

if __name__ == "__main__":

    policy = hstrat.recency_proportional_resolution_algo.Policy(3)

    col = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
    )
    for __ in range(100):
        col.DepositStratum()

    print("export hereditary stragitraphic columns to pandas dataframe")
    print(hstrat.col_to_dataframe(col))
    print()

    # horizontal divider, adapted from https://stackoverflow.com/a/42762743
    os.system(r"""printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -""")

    with tempfile.NamedTemporaryFile("w+") as tmp:
        print(f"serialize column as json to file {tmp.name}")
        json.dump(hstrat.col_to_records(col), tmp, indent=4)
        tmp.flush()
        os.system(f"set -x; head -c 500 {tmp.name} | head -n 10")
        print("...")
        print("show file size")
        os.system(f"set -x; du -b {tmp.name}")
        print()

        tmp.seek(0)
        deserialized = hstrat.col_from_records(json.load(tmp))
        print(f"deserialized and original equal? {deserialized == col}")
        print()

    # horizontal divider, adapted from https://stackoverflow.com/a/42762743
    os.system(r"""printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -""")

    with tempfile.NamedTemporaryFile("w+") as tmp:
        print(f"serialize column as yaml to file {tmp.name}")
        yaml.dump(hstrat.col_to_records(col), tmp)
        tmp.flush()
        os.system(f"set -x; head -c 500 {tmp.name} | head -n 10")
        print("...")
        print("show file size")
        os.system(f"set -x; du -b {tmp.name}")
        print()

        tmp.seek(0)
        deserialized = hstrat.col_from_records(yaml.safe_load(tmp))
        print(f"deserialized and original equal? {deserialized == col}")
        print()

    # horizontal divider, adapted from https://stackoverflow.com/a/42762743
    os.system(r"""printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -""")

    with tempfile.NamedTemporaryFile("w+b") as tmp:
        tmp_gz = gzip.GzipFile(mode="w+b", fileobj=tmp)
        print(f"serialize column as json to file {tmp.name} with gzip")
        json.dump(hstrat.col_to_records(col), io.TextIOWrapper(tmp_gz))
        tmp.flush()
        os.system(
            f"set -x; cat {tmp.name} | gunzip | head -c 500 | head -n 10"
        )
        print("...")
        print("show file size")
        os.system(f"set -x; du -b {tmp.name}")
        print()

        with gzip.open(tmp.name, "r") as tmp_gz_in:
            records = json.load(io.TextIOWrapper(tmp_gz_in))
            deserialized = hstrat.col_from_records(records)
            print(f"deserialized and original equal? {deserialized == col}")
