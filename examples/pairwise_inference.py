#!/usr/bin/env python3

from hstrat import hstrat

if __name__ == "__main__":

    print("creating founder1 and founder2, which share no ancestry...")
    founder1 = hstrat.HereditaryStratigraphicColumn(
        # retain strata from every generation
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(1)
    )
    founder2 = hstrat.HereditaryStratigraphicColumn(
        # retain strata from every third generation
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(3),
    )

    print(
        "   ",
        "do founder1 and founder2 share any common ancestor?",
        hstrat.does_have_any_common_ancestor(founder1, founder2),
    )

    print()
    print("creating child1 from founder1...")
    child1 = founder1.CloneDescendant()

    print(
        "   ",
        "do founder1 and child1 share any common ancestor?",
        hstrat.does_have_any_common_ancestor(founder1, child1),
    )

    print(
        "   ",
        "do founder2 and child1 share any common ancestor?",
        hstrat.does_have_any_common_ancestor(founder2, child1),
    )

    print()
    print("creating descendant1a, 10 generations removed from founder1...")
    descendant1a = founder1.Clone()
    for __ in range(10):
        descendant1a.DepositStratum()

    print("creating descendant1b, 50 generations removed from founder1...")
    descendant1b = founder1.Clone()
    for __ in range(50):
        descendant1b.DepositStratum()

    print(
        "   ",
        "estimate descendant1a generations since MRCA with descendant1b?",
        hstrat.calc_ranks_since_mrca_bounds_with(
            descendant1a, descendant1b, prior="arbitrary"
        ),
    )
    print(
        "   ",
        "estimate descendant1b generations since MRCA with descendant1a?",
        hstrat.calc_ranks_since_mrca_bounds_with(
            descendant1b, descendant1a, prior="arbitrary"
        ),
    )
    print(
        "estimate generation of MRCA between descendant1a and descendant1b?",
        hstrat.calc_rank_of_mrca_bounds_between(
            descendant1a, descendant1b, prior="arbitrary"
        ),
    )

    print()
    print("creating descendant2a, 10 generations removed from founder2...")
    descendant2a = founder2.Clone()
    for __ in range(10):
        descendant2a.DepositStratum()
    print("creating descendant2b, 20 generations removed from descendant2a...")
    descendant2b = descendant2a.Clone()
    for __ in range(20):
        descendant2b.DepositStratum()
    print("creating descendant2c, 5 generations removed from descendant2a...")
    descendant2c = descendant2a.Clone()
    for __ in range(5):
        descendant2c.DepositStratum()

    print(
        "   ",
        "estimate descendant2b generations since MRCA with descendant2c?",
        hstrat.calc_ranks_since_mrca_bounds_with(
            descendant2b, descendant2c, prior="arbitrary"
        ),
    )
    print(
        "   ",
        "estimate descendant2c generations since MRCA with descendant2b?",
        hstrat.calc_ranks_since_mrca_bounds_with(
            descendant2c, descendant2b, prior="arbitrary"
        ),
    )
    print(
        "   ",
        "estimate generation of MRCA between descendant2b and descendant2c?",
        hstrat.calc_rank_of_mrca_bounds_between(
            descendant2b, descendant2c, prior="arbitrary"
        ),
    )
    print(
        "    ^^^ "
        "note MRCA estimate uncertainty, "
        "caused by sparser stratum retention policy"
    )
