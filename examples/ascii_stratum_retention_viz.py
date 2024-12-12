#!/usr/bin/env python3

from hstrat import hstrat

if __name__ == "__main__":

    for policy in (
        hstrat.fixed_resolution_algo.Policy(3),
        hstrat.recency_proportional_resolution_algo.Policy(3),
    ):
        print()
        print(policy)

        col = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
        )
        for __ in range(20):
            col.DepositStratum()

        print(hstrat.col_to_ascii(col))
