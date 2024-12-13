#!/usr/bin/env python3
# note: temporarily disabled because failing on gh actions build as "cancelled"

import gzip
import io
import json
import os
import random
import tempfile

import yaml

from hstrat import hstrat

if __name__ == "__main__":

    policy = hstrat.recency_proportional_resolution_algo.Policy(3)

    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
    )
    pop = [common_ancestor.CloneDescendant() for __ in range(10)]

    for __ in range(100):
        target = random.randrange(len(pop))
        pop[target] = random.choice(pop).CloneDescendant()

    print(
        "export population of hereditary stratigraphic columns "
        "to pandas dataframe"
    )
    print(hstrat.pop_to_dataframe(pop))
    print()

    # horizontal divider, adapted from https://stackoverflow.com/a/42762743
    os.system(r"""printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -""")

    with tempfile.NamedTemporaryFile("w+") as tmp:
        print(f"serialize population as json to file {tmp.name}")
        json.dump(hstrat.pop_to_records(pop), tmp, indent=4)
        tmp.flush()
        os.system(f"set -x; head -c 500 {tmp.name} | head -n 10")
        print("...")
        print("show file size")
        os.system(f"set -x; du -b {tmp.name}")
        print()

        tmp.seek(0)
        deserialized = hstrat.pop_from_records(json.load(tmp))
        print(f"deserialized and original equal? {deserialized == pop}")
        print()

    # horizontal divider, adapted from https://stackoverflow.com/a/42762743
    os.system(r"""printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -""")

    with tempfile.NamedTemporaryFile("w+") as tmp:
        print(f"serialize population as yaml to file {tmp.name}")
        yaml.dump(hstrat.pop_to_records(pop), tmp)
        tmp.flush()
        os.system(f"set -x; head -c 500 {tmp.name} | head -n 10")
        print("...")
        print("show file size")
        os.system(f"set -x; du -b {tmp.name}")
        print()

        tmp.seek(0)
        deserialized = hstrat.pop_from_records(yaml.safe_load(tmp))
        print(f"deserialized and original equal? {deserialized == pop}")
        print()

    # horizontal divider, adapted from https://stackoverflow.com/a/42762743
    os.system(r"""printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -""")

    with tempfile.NamedTemporaryFile("w+b") as tmp:
        tmp_gz = gzip.GzipFile(mode="w+b", fileobj=tmp)
        print(f"serialize population as json to file {tmp.name} with gzip")
        json.dump(hstrat.pop_to_records(pop), io.TextIOWrapper(tmp_gz))
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
            deserialized = hstrat.pop_from_records(records)
            print(f"deserialized and original equal? {deserialized == pop}")
