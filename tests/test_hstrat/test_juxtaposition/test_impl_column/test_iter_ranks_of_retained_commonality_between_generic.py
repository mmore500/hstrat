import itertools as it
import random

import pytest

from hstrat import hstrat
from hstrat.juxtaposition._impl_column import (
    iter_ranks_of_retained_commonality_between,
)


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreTree,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_comparison_commutativity_asynchronous(
    retention_policy,
    ordered_store,
):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for _generation in range(100):
        _ = _generation
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert [
                *iter_ranks_of_retained_commonality_between(first, second)
            ] == [*iter_ranks_of_retained_commonality_between(second, first)]

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].CloneDescendant()
        for individual in population:
            # asynchronous generations
            if random.choice([True, False]):
                individual.DepositStratum()


@pytest.mark.parametrize(
    "retention_policy",
    [
        pytest.param(
            hstrat.perfect_resolution_algo.Policy(),
            marks=pytest.mark.heavy_2a,
        ),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreDict,
            marks=pytest.mark.heavy_2b,
        ),
        hstrat.HereditaryStratumOrderedStoreList,
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreTree,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_comparison_commutativity_synchronous(
    retention_policy,
    ordered_store,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for _generation in range(100):
        _ = _generation
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert [
                *iter_ranks_of_retained_commonality_between(first, second)
            ] == [*iter_ranks_of_retained_commonality_between(second, first)]

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        # synchronous generations
        for individual in population:
            individual.DepositStratum()


# @pytest.mark.parametrize(
#     "retention_policy1",
#     [
#         hstrat.perfect_resolution_algo.Policy(),
#         hstrat.nominal_resolution_algo.Policy(),
#         hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
#     ],
# )
# @pytest.mark.parametrize(
#     "retention_policy2",
#     [
#         hstrat.perfect_resolution_algo.Policy(),
#         hstrat.nominal_resolution_algo.Policy(),
#         hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
#     ],
# )
# @pytest.mark.parametrize(
#     "ordered_store",
#     [
#         hstrat.HereditaryStratumOrderedStoreDict,
#         hstrat.HereditaryStratumOrderedStoreList,
#         hstrat.HereditaryStratumOrderedStoreTree,
#     ],
# )
# def test_scenario_no_mrca(
#     retention_policy1,
#     retention_policy2,
#     ordered_store,
# ):
#     first = hstrat.HereditaryStratigraphicColumn(
#         stratum_ordered_store=ordered_store,
#         stratum_retention_policy=retention_policy1,
#     )
#     second = hstrat.HereditaryStratigraphicColumn(
#         stratum_ordered_store=ordered_store,
#         stratum_retention_policy=retention_policy2,
#     )
#
#     for generation in range(100):
#         assert (
#             hstrat.calc_rank_of_last_retained_commonality_between(
#                 first, second
#             )
#             is None
#         )
#         assert (
#             hstrat.calc_rank_of_last_retained_commonality_between(
#                 second, first
#             )
#             is None
#         )
#
#         first.DepositStratum()
#         second.DepositStratum()
#

# @pytest.mark.parametrize(
#     "retention_policy",
#     [
#         hstrat.perfect_resolution_algo.Policy(),
#         hstrat.nominal_resolution_algo.Policy(),
#         hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
#     ],
# )
# @pytest.mark.parametrize(
#     "ordered_store",
#     [
#         hstrat.HereditaryStratumOrderedStoreDict,
#         hstrat.HereditaryStratumOrderedStoreList,
#         hstrat.HereditaryStratumOrderedStoreTree,
#     ],
# )
# def test_scenario_no_divergence(retention_policy, ordered_store):
#     column = hstrat.HereditaryStratigraphicColumn(
#         stratum_ordered_store=ordered_store,
#         stratum_retention_policy=retention_policy,
#     )
#
#     for generation in range(100):
#         assert (
#             hstrat.calc_rank_of_last_retained_commonality_between(
#                 column, column
#             )
#             == generation
#         )
#
#         column.DepositStratum()
#
#
# @pytest.mark.parametrize(
#     "retention_policy",
#     [
#         hstrat.perfect_resolution_algo.Policy(),
#         hstrat.nominal_resolution_algo.Policy(),
#         hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
#     ],
# )
# @pytest.mark.parametrize(
#     "ordered_store",
#     [
#         hstrat.HereditaryStratumOrderedStoreDict,
#         hstrat.HereditaryStratumOrderedStoreList,
#         hstrat.HereditaryStratumOrderedStoreTree,
#     ],
# )
# def test_scenario_partial_even_divergence(retention_policy, ordered_store):
#     first = hstrat.HereditaryStratigraphicColumn(
#         stratum_ordered_store=ordered_store,
#         stratum_retention_policy=retention_policy,
#     )
#
#     for generation in range(100):
#         first.DepositStratum()
#
#     second = first.Clone()
#
#     first.DepositStratum()
#     second.DepositStratum()
#
#     for generation in range(101, 200):
#         assert (
#             0
#             <= hstrat.calc_rank_of_last_retained_commonality_between(
#                 first, second
#             )
#             <= 100
#         )
#
#         first.DepositStratum()
#         second.DepositStratum()
#
#
# @pytest.mark.parametrize(
#     "retention_policy",
#     [
#         hstrat.perfect_resolution_algo.Policy(),
#         hstrat.nominal_resolution_algo.Policy(),
#         hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
#     ],
# )
# @pytest.mark.parametrize(
#     "ordered_store",
#     [
#         hstrat.HereditaryStratumOrderedStoreDict,
#         hstrat.HereditaryStratumOrderedStoreList,
#         pytest.param(
#             hstrat.HereditaryStratumOrderedStoreTree,
#             marks=pytest.mark.heavy,
#         ),
#     ],
# )
# def test_scenario_partial_uneven_divergence(retention_policy, ordered_store):
#     first = hstrat.HereditaryStratigraphicColumn(
#         stratum_ordered_store=ordered_store,
#         stratum_retention_policy=retention_policy,
#     )
#
#     for generation in range(100):
#         first.DepositStratum()
#
#     second = first.Clone()
#
#     first.DepositStratum()
#
#     for generation in range(101, 200):
#         assert (
#             0
#             <= hstrat.calc_rank_of_last_retained_commonality_between(
#                 first, second
#             )
#             <= 100
#         )
#
#         first.DepositStratum()
#
#     second.DepositStratum()
#
#     for generation in range(101, 200):
#         assert (
#             0
#             <= hstrat.calc_rank_of_last_retained_commonality_between(
#                 first, second
#             )
#             <= 100
#         )
#
#         second.DepositStratum()
#
#
# @pytest.mark.parametrize(
#     "retention_policy",
#     [
#         hstrat.perfect_resolution_algo.Policy(),
#         hstrat.nominal_resolution_algo.Policy(),
#         hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
#     ],
# )
# @pytest.mark.parametrize(
#     "differentia_width",
#     [1, 2, 8],
# )
# def _do_test_IterRanksOfRetainedCommonalityBetweenGenerich1(
#     ordered_store,
#     differentia_width,
# ):
#     column = hstrat.HereditaryStratigraphicColumn(
#         stratum_differentia_bit_width=differentia_width,
#         stratum_ordered_store=ordered_store,
#     )
#
#     for generation in range(100):
#         column.DepositStratum()
#
#     offspring1 = column.CloneDescendant()
#     offspring2 = column.CloneDescendant()
#
#     for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
#         if differentia_width == 64:
#             assert (
#                 hstrat.calc_rank_of_last_retained_commonality_between(
#                     c1,
#                     c2,
#                 )
#                 == column.GetNumStrataDeposited() - 1
#             )
#             assert (
#                 hstrat.calc_rank_of_last_retained_commonality_between(
#                     c2,
#                     c1,
#                 )
#                 == column.GetNumStrataDeposited() - 1
#             )
#         elif differentia_width == 1:
#             assert (
#                 hstrat.calc_rank_of_last_retained_commonality_between(
#                     c1,
#                     c2,
#                 )
#                 < column.GetNumStrataDeposited() - 1
#             )
#             assert (
#                 hstrat.calc_rank_of_last_retained_commonality_between(
#                     c2,
#                     c1,
#                 )
#                 < column.GetNumStrataDeposited() - 1
#             )
#
#     for c in [column, offspring1, offspring2]:
#         assert hstrat.calc_rank_of_last_retained_commonality_between(
#             c, c, 0.8
#         ) == c.GetNumStrataDeposited() - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
#             significance_level=0.2,
#         )
#         assert hstrat.calc_rank_of_last_retained_commonality_between(
#             c, c, 0.99
#         ) == c.GetNumStrataDeposited() - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
#             significance_level=0.01,
#         )
#
#     for generation in range(100):
#         offspring1.DepositStratum()
#         offspring2.DepositStratum()
#
#     for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
#         if differentia_width == 64:
#             assert (
#                 hstrat.calc_rank_of_last_retained_commonality_between(
#                     c1,
#                     c2,
#                 )
#                 == column.GetNumStrataDeposited() - 1
#             )
#             assert (
#                 hstrat.calc_rank_of_last_retained_commonality_between(
#                     c2,
#                     c1,
#                 )
#                 == column.GetNumStrataDeposited() - 1
#             )
#         elif differentia_width == 1:
#             assert hstrat.calc_rank_of_last_retained_commonality_between(
#                 c1, c2, 0.999999
#             ) < hstrat.calc_rank_of_last_retained_commonality_between(
#                 c2, c1, 0.8
#             )
#
#     for c in [column, offspring1, offspring2]:
#         assert hstrat.calc_rank_of_last_retained_commonality_between(
#             c, c, 0.8
#         ) == c.GetNumStrataDeposited() - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
#             significance_level=0.2,
#         )
#         assert hstrat.calc_rank_of_last_retained_commonality_between(
#             c, c, 0.99
#         ) == c.GetNumStrataDeposited() - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
#             significance_level=0.01,
#         )
#
#
# @pytest.mark.parametrize(
#     "ordered_store",
#     [
#         hstrat.HereditaryStratumOrderedStoreDict,
#         hstrat.HereditaryStratumOrderedStoreList,
#         hstrat.HereditaryStratumOrderedStoreTree,
#     ],
# )
# def test_IterRanksOfRetainedCommonalityBetweenGenerich2(ordered_store):
#     column = hstrat.HereditaryStratigraphicColumn(
#         stratum_differentia_bit_width=1,
#     )
#
#     while True:
#         offspring1 = column.CloneDescendant()
#         offspring2 = column.CloneDescendant()
#
#         res = hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring1,
#             offspring2,
#         )
#         assert res is None
#         assert res == hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring2,
#             offspring1,
#         )
#         for gen in range(10):
#             offspring1.DepositStratum()
#             offspring2.DepositStratum()
#
#         # should happen about every 1 in 20 times
#         if (
#             hstrat.calc_rank_of_last_retained_commonality_between(
#                 offspring2,
#                 offspring1,
#             )
#             is not None
#         ):
#             break
#
#     column = hstrat.HereditaryStratigraphicColumn(
#         stratum_differentia_bit_width=1,
#     )
#
#     for __ in range(100):
#         column.DepositStratum()
#
#     for rep in range(5):
#         offspring1 = column.CloneDescendant()
#         offspring2 = column.CloneDescendant()
#
#         res = hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring1,
#             offspring2,
#         )
#         assert res is not None
#         assert res == hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring2,
#             offspring1,
#         )
#
#         for gen in range(10):
#             offspring1.DepositStratum()
#             offspring2.DepositStratum()
#
#         res = hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring1,
#             offspring2,
#         )
#         assert res is not None
#         assert res == hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring2,
#             offspring1,
#         )
#
#
# @pytest.mark.parametrize(
#     "ordered_store",
#     [
#         hstrat.HereditaryStratumOrderedStoreDict,
#         hstrat.HereditaryStratumOrderedStoreList,
#         hstrat.HereditaryStratumOrderedStoreTree,
#     ],
# )
# def test_IterRanksOfRetainedCommonalityBetweenGenerich3(ordered_store):
#     column = hstrat.HereditaryStratigraphicColumn(
#         stratum_differentia_bit_width=64,
#         stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
#     )
#
#     for generation in range(100):
#         column.DepositStratum()
#
#     offspring1 = column.CloneDescendant()
#     offspring2 = column.CloneDescendant()
#
#     for generation in range(100):
#         offspring1.DepositStratum()
#         offspring2.DepositStratum()
#
#     for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
#         assert c1.GetNumStrataRetained() == 2
#         assert c2.GetNumStrataRetained() == 2
#
#         assert (
#             hstrat.calc_rank_of_last_retained_commonality_between(
#                 c1,
#                 c2,
#             )
#             == 0
#         )
#         assert (
#             hstrat.calc_rank_of_last_retained_commonality_between(
#                 c2,
#                 c1,
#             )
#             == 0
#         )
#
#
# @pytest.mark.parametrize(
#     "ordered_store",
#     [
#         hstrat.HereditaryStratumOrderedStoreDict,
#         hstrat.HereditaryStratumOrderedStoreList,
#         hstrat.HereditaryStratumOrderedStoreTree,
#     ],
# )
# def test_IterRanksOfRetainedCommonalityBetweenGenerich4(ordered_store):
#     column = hstrat.HereditaryStratigraphicColumn(
#         stratum_differentia_bit_width=1,
#         stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
#     )
#
#     while True:
#         offspring1 = column.CloneDescendant()
#         offspring2 = column.CloneDescendant()
#
#         res = hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring1,
#             offspring2,
#         )
#         assert res is None
#         assert res == hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring2,
#             offspring1,
#         )
#         for gen in range(10):
#             offspring1.DepositStratum()
#             offspring2.DepositStratum()
#
#         # should happen about every 1 in 20 times
#         if (
#             hstrat.calc_rank_of_last_retained_commonality_between(
#                 offspring2,
#                 offspring1,
#             )
#             is not None
#         ):
#             break
#
#     column = hstrat.HereditaryStratigraphicColumn(
#         stratum_differentia_bit_width=1,
#         stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
#     )
#
#     for __ in range(100):
#         column.DepositStratum()
#
#     for rep in range(5):
#         offspring1 = column.CloneDescendant()
#         offspring2 = column.CloneDescendant()
#
#         res = hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring1,
#             offspring2,
#         )
#         assert res is not None
#         assert res == hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring2,
#             offspring1,
#         )
#
#         for gen in range(10):
#             offspring1.DepositStratum()
#             offspring2.DepositStratum()
#
#         res = hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring1,
#             offspring2,
#         )
#         assert res is not None
#         assert res == hstrat.calc_rank_of_last_retained_commonality_between(
#             offspring2,
#             offspring1,
#         )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8],
)
def test_IterRanksOfRetainedCommonalityBetweenGenerich5(
    ordered_store,
    differentia_width,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_width,
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
    )

    column.DepositStrata(100)

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    assert column.GetNumStrataDeposited() == 101
    assert offspring1.GetNumStrataDeposited() == 102
    assert offspring2.GetNumStrataDeposited() == 102

    for c1, c2 in it.permutations([column, offspring1, offspring2], 2):
        if differentia_width == 64 or c1 is column or c2 is column:
            assert [
                *iter_ranks_of_retained_commonality_between(
                    c1,
                    c2,
                )
            ] == [*column.IterRetainedRanks()]
        else:
            assert all(
                rank >= column.GetNumStrataDeposited()
                and rank in c1.IterRetainedRanks()
                and rank in c2.IterRetainedRanks()
                for rank in (
                    set(
                        iter_ranks_of_retained_commonality_between(
                            c1,
                            c2,
                        )
                    )
                )
                - set(column.IterRetainedRanks())
            )

        assert all(
            rank in set(c1.IterRetainedRanks()) & set(c2.IterRetainedRanks())
            for rank in iter_ranks_of_retained_commonality_between(c2, c1)
        )
        assert all(
            (
                c1.GetStratumAtRank(rank).GetDifferentia()
                == c2.GetStratumAtRank(rank).GetDifferentia()
            )
            == (rank in iter_ranks_of_retained_commonality_between(c2, c1))
            for rank in (
                set(c1.IterRetainedRanks()) & set(c2.IterRetainedRanks())
            )
        )

    offspring1.DepositStrata(99)
    offspring2.DepositStrata(99)

    for c1, c2 in it.permutations([column, offspring1, offspring2], 2):
        if differentia_width == 64 or c1 is column or c2 is column:
            assert [
                *iter_ranks_of_retained_commonality_between(
                    c1,
                    c2,
                )
            ] == [*column.IterRetainedRanks()]
        else:
            assert all(
                rank >= column.GetNumStrataDeposited()
                and rank in c1.IterRetainedRanks()
                and rank in c2.IterRetainedRanks()
                for rank in (
                    set(
                        iter_ranks_of_retained_commonality_between(
                            c1,
                            c2,
                        )
                    )
                )
                - set(column.IterRetainedRanks())
            )

        assert all(
            rank in set(c1.IterRetainedRanks()) & set(c2.IterRetainedRanks())
            for rank in iter_ranks_of_retained_commonality_between(c2, c1)
        )
        assert all(
            all(
                c1.GetStratumAtRank(r).GetDifferentia()
                == c2.GetStratumAtRank(r).GetDifferentia()
                for r in (
                    set(c1.IterRetainedRanks()) & set(c2.IterRetainedRanks())
                )
                if r <= rank
            )
            == (rank in iter_ranks_of_retained_commonality_between(c2, c1))
            for rank in (
                set(c1.IterRetainedRanks()) & set(c2.IterRetainedRanks())
            )
        )
