from copy import deepcopy
from iterpop import iterpop as ip
from iterify import cyclify, iterify
import itertools as it
import opytional as opyt
import random
import unittest

from pylib import hstrat

random.seed(1)


def _do_test_Clone1(
    testcase,
    retention_predicate,
    ordered_store,
):
    original1 = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )
    original1_copy1 = deepcopy(original1)
    original1_copy2 = original1.Clone()

    assert original1 == original1_copy1
    assert original1 == original1_copy2
    assert original1_copy1 == original1_copy2

    for first in original1, original1_copy1, original1_copy2:
        for second in original1, original1_copy1, original1_copy2:
            assert first.HasAnyCommonAncestorWith(second)


def _do_test_Clone2(
    testcase,
    retention_predicate,
    ordered_store,
):
    original2 = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_predicate=retention_predicate,
    )
    original2.DepositStratum()
    original2.DepositStratum()

    original2_copy1 = deepcopy(original2)
    original2_copy2 = original2.Clone()

    for which in original2, original2_copy1, original2_copy2:
        for __ in range(20):
            which.DepositStratum()

    for first in original2, original2_copy1, original2_copy2:
        for second in original2, original2_copy1, original2_copy2:
            assert first.HasAnyCommonAncestorWith(second)

def _do_test_Clone3(
    testcase,
    retention_predicate,
    ordered_store,
):

    column = hstrat.HereditaryStratigraphicColumn(
        initial_stratum_annotation=0,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate
            =hstrat.StratumRetentionPredicatePerfectResolution(),
    )
    population = [
        column.Clone()
        for __ in range(3)
    ]

    for generation in range(100):

        for f, s in it.combinations(population, 2):
            assert not f.HasDiscardedStrata()
            assert not s.HasDiscardedStrata()
            assert f.HasAnyCommonAncestorWith(s)
            assert f.GetLastCommonStratumWith(
                s,
            ) is not None, (retention_predicate, generation, f.GetNumStrataDeposited(), s.GetNumStrataDeposited())


        # advance generation
        population[0] = population[0].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


def _do_test_Clone3(
    testcase,
    retention_predicate,
    ordered_store,
):
    # regression test for bug with tree store cloning
    column = hstrat.HereditaryStratigraphicColumn(
        initial_stratum_annotation=0,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate
            =hstrat.StratumRetentionPredicatePerfectResolution(),
    )
    population = [
        column.Clone()
        for __ in range(3)
    ]

    for generation in range(100):

        for f, s in it.combinations(population, 2):
            assert not f.HasDiscardedStrata()
            assert f.HasAnyCommonAncestorWith(s)
            assert f.GetLastCommonStratumWith(s) is not None

        # advance generation
        population[0] = population[0].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


def _do_test_equality(
    testcase,
    retention_predicate,
    ordered_store,
):

    original1 = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )
    copy1 = deepcopy(original1)
    copy2 = original1.Clone()
    original2 = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_predicate=retention_predicate,
    )

    assert original1 == copy1
    assert original1 == copy2
    assert copy1 == copy2
    assert original1 != original2
    assert copy1 != original2
    assert copy2 != original2

    copy1.DepositStratum()
    assert original1 != copy1

    original1.DepositStratum()
    assert original1 != copy1


def _do_test_comparison_commutativity_asyncrhonous(
    testcase,
    retention_predicate,
    ordered_store,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_predicate=retention_predicate,
        )
        for __ in range(10)
    ]

    for generation in range(100):

        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert (
                first.CalcRankOfLastRetainedCommonalityWith(second)
                == second.CalcRankOfLastRetainedCommonalityWith(first)
            )
            assert (
                first.CalcRankOfFirstRetainedDisparityWith(second)
                == second.CalcRankOfFirstRetainedDisparityWith(first)
            )
            assert (
                first.CalcRankOfMrcaBoundsWith(second)
                == second.CalcRankOfMrcaBoundsWith(first)
            )
            assert (
                first.CalcRankOfMrcaUncertaintyWith(second)
                == second.CalcRankOfMrcaUncertaintyWith(first)
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].CloneDescendant()
        for individual in population:
            # asynchronous generations
            if random.choice([True, False]):
                individual.DepositStratum()


def _do_test_annotation(
    testcase,
    retention_predicate,
    ordered_store,
):

    column = hstrat.HereditaryStratigraphicColumn(
        initial_stratum_annotation=0,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )
    population = [
        column.Clone()
        for __ in range(10)
    ]

    for generation in range(100):

        for f, s in it.combinations(population, 2):

            lb, ub = f.CalcRankOfMrcaBoundsWith(s)
            assert (
                lb <= f.GetLastCommonStratumWith(s).GetAnnotation() < ub
            )
            assert (
                lb <= s.GetLastCommonStratumWith(f).GetAnnotation() < ub
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        for individual in population:
            individual.DepositStratum(
                annotation=generation + 1,
            )


def _do_test_CalcRankOfMrcaBoundsWith(
    testcase,
    retention_predicate,
    ordered_store,
):
    def make_bundle():
        return hstrat.HereditaryStratigraphicColumnBundle({
            'test' : hstrat.HereditaryStratigraphicColumn(
                initial_stratum_annotation=0,
                stratum_ordered_store_factory=ordered_store,
                stratum_retention_predicate=retention_predicate,
            ),
            'control' : hstrat.HereditaryStratigraphicColumn(
                initial_stratum_annotation=0,
                stratum_ordered_store_factory=ordered_store,
                stratum_retention_condemner
                    =hstrat.StratumRetentionCondemnerPerfectResolution(),
            ),
        })

    column = make_bundle()
    frozen_copy = column.Clone()
    frozen_unrelated = make_bundle()
    population = [
        column.Clone()
        for __ in range(10)
    ]
    forked_isolated = column.Clone()
    unrelated_isolated = make_bundle()

    for generation in range(100):

        for f, s in it.chain(
            it.combinations(population, 2),
            zip(population, cyclify(forked_isolated)),
            zip(population, cyclify(frozen_copy)),
            zip(cyclify(forked_isolated), population),
            zip(cyclify(frozen_copy), population),
        ):
            lb, ub = f['test'].CalcRankOfMrcaBoundsWith(s['test'])
            actual_rank_of_mrca = f['control'].GetLastCommonStratumWith(
                s['control'],
            ).GetAnnotation()
            assert lb <= actual_rank_of_mrca < ub

        for f, s in it.chain(
            zip(population, cyclify(frozen_unrelated)),
            zip(population, cyclify(unrelated_isolated)),
            zip(cyclify(frozen_unrelated), population),
            zip(cyclify(unrelated_isolated), population),
        ):
            assert f['test'].CalcRankOfMrcaBoundsWith(s['test']) is None

        # advance generation
        random.shuffle(population)
        for target in range(3):
            population[target] = population[-1].CloneDescendant(
                stratum_annotation=population[-1].GetNumStrataDeposited(),
            )
        for individual in it.chain(
            iter(population),
            iterify(forked_isolated),
            iterify(unrelated_isolated),
        ):
            if random.choice([True, False]):
                individual.DepositStratum(
                    annotation=individual.GetNumStrataDeposited(),
                )

def _do_test_CalcRanksSinceMrcaBoundsWith(
    testcase,
    retention_predicate,
    ordered_store,
):
    def make_bundle():
        return hstrat.HereditaryStratigraphicColumnBundle({
            'test' : hstrat.HereditaryStratigraphicColumn(
                initial_stratum_annotation=0,
                stratum_ordered_store_factory=ordered_store,
                stratum_retention_predicate=retention_predicate,
            ),
            'control' : hstrat.HereditaryStratigraphicColumn(
                initial_stratum_annotation=0,
                stratum_ordered_store_factory=ordered_store,
                stratum_retention_condemner
                    =hstrat.StratumRetentionCondemnerPerfectResolution(),
            ),
        })

    column = make_bundle()
    frozen_copy = column.Clone()
    frozen_unrelated = make_bundle()
    population = [
        column.Clone()
        for __ in range(10)
    ]
    forked_isolated = column.Clone()
    unrelated_isolated = make_bundle()

    for generation in range(100):

        for f, s in it.chain(
            it.combinations(population, 2),
            zip(population, cyclify(forked_isolated)),
            zip(population, cyclify(frozen_copy)),
            zip(cyclify(forked_isolated), population),
            zip(cyclify(frozen_copy), population),
        ):
            lb, ub = f['test'].CalcRanksSinceMrcaBoundsWith(s['test'])
            actual_rank_of_mrca = f['control'].GetLastCommonStratumWith(
                s['control'],
            ).GetAnnotation()
            actual_ranks_since_mrca = (
                f.GetNumStrataDeposited() - actual_rank_of_mrca - 1
            )
            assert lb <= actual_ranks_since_mrca < ub

        for f, s in it.chain(
            zip(population, cyclify(frozen_unrelated)),
            zip(population, cyclify(unrelated_isolated)),
            zip(cyclify(frozen_unrelated), population),
            zip(cyclify(unrelated_isolated), population),
        ):
            assert f['test'].CalcRanksSinceMrcaBoundsWith(s['test']) is None

        # advance generation
        random.shuffle(population)
        for target in range(3):
            population[target] = population[-1].Clone()
            population[target].DepositStratum(
                annotation=population[target].GetNumStrataDeposited(),
            )
        for individual in it.chain(
            iter(population),
            iterify(forked_isolated),
            iterify(unrelated_isolated),
        ):
            if random.choice([True, False]):
                individual.DepositStratum(
                    annotation=individual.GetNumStrataDeposited(),
                )

def _do_test_comparison_commutativity_syncrhonous(
    testcase,
    retention_predicate,
    ordered_store,
):

    population = [
            hstrat.HereditaryStratigraphicColumn(
                stratum_ordered_store_factory=ordered_store,
                stratum_retention_predicate=retention_predicate,
            )
        for __ in range(10)
    ]

    for generation in range(100):

        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert (
                first.CalcRankOfLastRetainedCommonalityWith(second)
                == second.CalcRankOfLastRetainedCommonalityWith(first)
            )
            assert (
                first.CalcRankOfFirstRetainedDisparityWith(second)
                == second.CalcRankOfFirstRetainedDisparityWith(first)
            )
            assert (
                first.CalcRankOfMrcaBoundsWith(second)
                == second.CalcRankOfMrcaBoundsWith(first)
            )
            assert (
                first.CalcRankOfMrcaUncertaintyWith(second)
                == second.CalcRankOfMrcaUncertaintyWith(first)
            )
            assert (
                first.CalcRanksSinceLastRetainedCommonalityWith(second)
                == second.CalcRanksSinceLastRetainedCommonalityWith(first)
            )
            assert (
                first.CalcRanksSinceFirstRetainedDisparityWith(second)
                == second.CalcRanksSinceFirstRetainedDisparityWith(first)
            )
            assert (
                first.CalcRanksSinceMrcaBoundsWith(second)
                == second.CalcRanksSinceMrcaBoundsWith(first)
            )
            assert (
                first.CalcRanksSinceMrcaUncertaintyWith(second)
                == second.CalcRanksSinceMrcaUncertaintyWith(first)
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        # synchronous generations
        for individual in population: individual.DepositStratum()


def _do_test_comparison_validity(
    testcase,
    retention_predicate,
    ordered_store,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_predicate=retention_predicate,
        )
        for __ in range(10)
    ]

    for generation in range(100):

        for first, second in it.combinations(population, 2):
            lcrw = first.CalcRankOfLastRetainedCommonalityWith(second)
            if lcrw is not None:
                assert 0 <= lcrw <= generation

            fdrw = first.CalcRankOfFirstRetainedDisparityWith(second)
            if fdrw is not None:
                assert 0 <= fdrw <= generation

            assert (
                first.CalcRankOfMrcaBoundsWith(second)
                in [
                    (
                        lcrw,
                        opyt.or_value(fdrw, first.GetNumStrataDeposited())
                    ),
                    None,
                ]
            )
            if lcrw is not None and fdrw is not None:
                assert lcrw < fdrw

            assert first.CalcRankOfMrcaUncertaintyWith(second) >= 0

            rslcw = first.CalcRanksSinceLastRetainedCommonalityWith(second)
            if rslcw is not None:
                assert 0 <= rslcw <= generation

            rsfdw = first.CalcRanksSinceFirstRetainedDisparityWith(second)
            if rsfdw is not None:
                assert -1 <= rsfdw <= generation

            assert (
                first.CalcRanksSinceMrcaBoundsWith(second) is None
                or first.CalcRanksSinceMrcaBoundsWith(second)
                    == (opyt.or_value(rsfdw, -1) + 1, rslcw + 1)
            )
            if rslcw is not None and rsfdw is not None:
                assert rsfdw < rslcw

            assert first.CalcRanksSinceMrcaUncertaintyWith(second) >= 0

        # advance generations asynchronously
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


def _do_test_scenario_no_mrca(
    testcase,
    retention_predicate1,
    retention_predicate2,
    ordered_store,
):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate1,
    )
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate2,
    )

    for generation in range(100):
        assert first.CalcRankOfLastRetainedCommonalityWith(second) == None
        assert second.CalcRankOfLastRetainedCommonalityWith(first) == None

        assert first.CalcRankOfFirstRetainedDisparityWith(second) == 0
        assert second.CalcRankOfFirstRetainedDisparityWith(first) == 0

        assert first.CalcRankOfMrcaUncertaintyWith(second) == 0
        assert second.CalcRankOfMrcaUncertaintyWith(first) == 0

        assert first.CalcRanksSinceLastRetainedCommonalityWith(second) == None
        assert second.CalcRanksSinceLastRetainedCommonalityWith(first) == None

        assert first.CalcRanksSinceFirstRetainedDisparityWith(second) == generation
        assert second.CalcRanksSinceFirstRetainedDisparityWith(first) == generation

        assert first.CalcRanksSinceMrcaUncertaintyWith(second) == 0
        assert second.CalcRanksSinceMrcaUncertaintyWith(first) == 0

        first.DepositStratum()
        second.DepositStratum()


def _do_test_scenario_no_divergence(
    testcase,
    retention_predicate,
    ordered_store,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )

    for generation in range(100):

        assert column.CalcRankOfLastRetainedCommonalityWith(column) \
            == generation
        assert column.CalcRankOfFirstRetainedDisparityWith(column) == None
        assert column.CalcRankOfMrcaUncertaintyWith(column) == 0

        assert column.CalcRanksSinceLastRetainedCommonalityWith(column) == 0
        assert column.CalcRanksSinceFirstRetainedDisparityWith(column) == None
        assert column.CalcRanksSinceMrcaUncertaintyWith(column) == 0

        column.DepositStratum()


def _do_test_scenario_partial_even_divergence(
    testcase,
    retention_predicate,
    ordered_store,
):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )

    for generation in range(100):
        first.DepositStratum()

    second = first.Clone()

    first.DepositStratum()
    second.DepositStratum()

    for generation in range(101, 200):
        assert (
            0
            <= first.CalcRankOfLastRetainedCommonalityWith(second)
            <= 100
        )
        assert (
            100
            <= first.CalcRankOfFirstRetainedDisparityWith(second)
            <= generation
        )
        assert (
            generation - 101
            < first.CalcRanksSinceLastRetainedCommonalityWith(second)
            <= generation
        )
        assert (
            0
            <= first.CalcRanksSinceFirstRetainedDisparityWith(second)
            < generation - 100
        )

        first.DepositStratum()
        second.DepositStratum()


def _do_test_scenario_partial_uneven_divergence(
    self,
    retention_predicate,
    ordered_store,
):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )

    for generation in range(100):
        first.DepositStratum()

    second = first.Clone()

    first.DepositStratum()

    for generation in range(101, 200):
        assert (
            0
            <= first.CalcRankOfLastRetainedCommonalityWith(second)
            <= 100
        )
        assert (
            100
            <= first.CalcRankOfFirstRetainedDisparityWith(second)
            <= generation
        )

        assert (
            generation - 101
            < first.CalcRanksSinceLastRetainedCommonalityWith(second)
            <= generation
        )
        assert (
            0
            <= second.CalcRanksSinceLastRetainedCommonalityWith(first)
            <= 100
        )
        assert (
            0
            <= first.CalcRanksSinceFirstRetainedDisparityWith(second)
            < generation - 100
        )
        assert (
            -1 == second.CalcRanksSinceFirstRetainedDisparityWith(first)
        )

        first.DepositStratum()

    second.DepositStratum()

    for generation in range(101, 200):
        assert (
            0
            <= first.CalcRankOfLastRetainedCommonalityWith(second)
            <= 100
        )
        assert (
            100
            <= first.CalcRankOfFirstRetainedDisparityWith(second)
            <= generation + 1
        )

        assert (
            100
            <= first.CalcRanksSinceLastRetainedCommonalityWith(second)
            <= 200
        )
        assert (
            0
            <= second.CalcRanksSinceLastRetainedCommonalityWith(first)
            <= generation
        )
        assert (
            0
            <= first.CalcRanksSinceFirstRetainedDisparityWith(second)
            < 100
        )
        assert (
            -1
            <= second.CalcRanksSinceFirstRetainedDisparityWith(first)
            < generation - 100
        )

        second.DepositStratum()


def _do_test_HasAnyCommonAncestorWith(
    self,
    retention_predicate,
    ordered_store,
):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )
    first_copy = first.Clone()
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )

    def assert_validity():
        assert first.HasAnyCommonAncestorWith(first)
        assert first_copy.HasAnyCommonAncestorWith(first_copy)
        assert first.HasAnyCommonAncestorWith(first_copy)
        assert first_copy.HasAnyCommonAncestorWith(first)

        assert not second.HasAnyCommonAncestorWith(first)
        assert not first.HasAnyCommonAncestorWith(second)
        assert not second.HasAnyCommonAncestorWith(first_copy)
        assert not first_copy.HasAnyCommonAncestorWith(second)

    assert_validity()
    first.DepositStratum()
    assert_validity()
    second.DepositStratum()
    assert_validity()
    first.DepositStratum()
    assert_validity()

    for __ in range(100):
        first_copy.DepositStratum()
        assert_validity()


def _do_test_DiffRetainedRanks(
    self,
    ordered_store,
):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate
            =hstrat.StratumRetentionPredicateNominalResolution(),
    )
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate
            =hstrat.StratumRetentionPredicatePerfectResolution(),
    )

    assert first.DiffRetainedRanks(second) == (set(), set())
    assert second.DiffRetainedRanks(first) == (set(), set())

    first.DepositStratum()
    assert first.DiffRetainedRanks(second) == ({1}, set())
    assert second.DiffRetainedRanks(first) == (set(), {1})

    second.DepositStratum()
    assert first.DiffRetainedRanks(second) == (set(), set())
    assert second.DiffRetainedRanks(first) == (set(), set())

    first.DepositStratum()
    assert first.DiffRetainedRanks(second) == ({2}, {1})
    assert second.DiffRetainedRanks(first) == ({1}, {2})

    second.DepositStratum()
    assert first.DiffRetainedRanks(second) == (set(), {1})
    assert second.DiffRetainedRanks(first) == ({1}, set())


def _do_test_always_store_rank_in_stratum(
    testcase,
    retention_predicate,
    ordered_store,
):
    first = hstrat.HereditaryStratigraphicColumn(
        always_store_rank_in_stratum=True,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )
    second = hstrat.HereditaryStratigraphicColumn(
        always_store_rank_in_stratum=False,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )

    assert not first._ShouldOmitStratumDepositionRank()
    assert first.GetStratumAtColumnIndex(0).GetDepositionRank() == 0
    if hasattr(retention_predicate, 'CalcRankAtColumnIndex'):
        assert second._ShouldOmitStratumDepositionRank()
        assert second.GetStratumAtColumnIndex(0).GetDepositionRank() is None
    else:
        assert not second._ShouldOmitStratumDepositionRank()
        assert second.GetStratumAtColumnIndex(0).GetDepositionRank() == 0

    for gen in range(100):
        assert first.DiffRetainedRanks(second) == (set(), set())

        first.DepositStratum()
        second.DepositStratum()


def _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith1(
    testcase,
    ordered_store,
    differentia_width,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_width,
        stratum_ordered_store_factory=ordered_store,
    )

    for generation in range(100): column.DepositStratum()

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert c1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c2,
            ) == column.GetNumStrataDeposited() - 1
            assert c2.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c1,
            ) == column.GetNumStrataDeposited() - 1
        else:
            assert c1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c2,
            ) >= column.GetNumStrataDeposited() - 1
            assert c2.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c1,
            ) >= column.GetNumStrataDeposited() - 1

    for c in [column, offspring1, offspring2]:
        assert c.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(c) \
            == c.GetNumStrataDeposited() - 1

    for generation in range(100):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert c1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c2,
            ) == column.GetNumStrataDeposited() - 1
            assert c2.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c1,
            ) == column.GetNumStrataDeposited() - 1
        else:
            assert c1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c2,
            ) >= column.GetNumStrataDeposited() - 1
            assert c2.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c1,
            ) >= column.GetNumStrataDeposited() - 1

    for c in [column, offspring1, offspring2]:
        assert c.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(c) \
            == c.GetNumStrataDeposited() - 1


def _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith2(
    testcase,
    ordered_store,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )

    while True:
        offspring1 = column.CloneDescendant()
        offspring2 = column.CloneDescendant()
        res = offspring1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
            offspring2,
        )
        if res is not None and res > column.GetNumStrataDeposited() - 1:
            assert offspring2.\
                CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                    offspring1,
                ) == res
            break


def _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith3(
    testcase,
    ordered_store,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
        stratum_retention_condemner
            =hstrat.StratumRetentionCondemnerNominalResolution(),
    )

    for generation in range(100): column.DepositStratum()

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    for generation in range(100):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        assert c1.GetNumStrataRetained() == 2
        assert c2.GetNumStrataRetained() == 2

        assert c1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
            c2,
        ) == 0
        assert c2.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
            c1,
        ) == 0


def _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith4(
    testcase,
    ordered_store,
):

    def do_once():
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        )

        res = c1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
            c2,
        )
        assert c2.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
            c1,
        ) == res
        assert res in (None, 0)

        if res is None:
            for generation in range(100):
                c1.DepositStratum()
                c2.DepositStratum()
            res = c1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(c2)
            assert res is None
            assert c2.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c1,
            ) is None
        elif res == 0:
            while True:
                c1_ = c1.CloneDescendant()
                c2_ = c2.CloneDescendant()
                if c1_.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                    c2_
                ) == 1: break

        return res

    while do_once() is not None: pass

    while do_once() != 0: pass

def _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith5(
    testcase,
    ordered_store,
):

    def do_once():
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_predicate
                =hstrat.StratumRetentionPredicateFixedResolution(2),
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_predicate
                =hstrat.StratumRetentionPredicateFixedResolution(2),
        )

        res = c1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
            c2,
        )
        assert c2.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
            c1,
        ) == res
        assert res in (None, 0)

        if res is None:
            for generation in range(100):
                c1.DepositStratum()
                c2.DepositStratum()
            res = c1.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(c2)
            assert res is None
            assert c2.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                c1,
            ) is None
        elif res == 0:
            while True:
                c1_ = c1.CloneDescendant()
                c2_ = c2.CloneDescendant()
                c1_.DepositStratum()
                c2_.DepositStratum()
                if c1_.CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
                    c2_
                ) == 2: break

        return res

    while do_once() is not None: pass

    while do_once() != 0: pass


class TestHereditaryStratigraphicColumn(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_GetNumStrataDeposited(self):
        column = hstrat.HereditaryStratigraphicColumn()
        for i in range(10):
            assert column.GetNumStrataDeposited() == i + 1
            column.DepositStratum()

    def test_CloneDescendant(self):
        column = hstrat.HereditaryStratigraphicColumn()
        assert column.GetNumStrataDeposited() == 1
        descendant = column.CloneDescendant(
            stratum_annotation='annotation'
        )
        assert descendant.GetNumStrataDeposited() == 2
        assert descendant.HasAnyCommonAncestorWith(column)
        assert column.GetNumStrataDeposited() == 1
        assert (
            descendant.GetStratumAtColumnIndex(
                descendant.GetNumStrataRetained() - 1
            ).GetAnnotation()
            == 'annotation'
        )

    def test_Clone(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_Clone1(
                    self,
                    retention_predicate,
                    ordered_store,
                )
                _do_test_Clone2(
                    self,
                    retention_predicate,
                    ordered_store,
                )
                _do_test_Clone3(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_equality(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_equality(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_comparison_commutativity_asyncrhonous(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_comparison_commutativity_asyncrhonous(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_annotation(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_annotation(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_CalcRankOfMrcaBoundsWith(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_CalcRankOfMrcaBoundsWith(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_CalcRanksSinceMrcaBoundsWith(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_CalcRanksSinceMrcaBoundsWith(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_comparison_commutativity_syncrhonous(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_comparison_commutativity_syncrhonous(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_comparison_validity(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_comparison_validity(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_scenario_no_mrca(self):
        for rp1, rp2 in it.product(
            [
                hstrat.StratumRetentionPredicatePerfectResolution(),
                hstrat.StratumRetentionPredicateNominalResolution(),
                hstrat.StratumRetentionPredicateDepthProportionalResolution(),
                hstrat.StratumRetentionPredicateFixedResolution(),
                hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
                hstrat.StratumRetentionPredicateStochastic(),
            ],
            repeat=2,
        ):
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_scenario_no_mrca(
                    self,
                    rp1,
                    rp2,
                    ordered_store,
                )

    def test_scenario_no_divergence(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_scenario_no_divergence(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_scenario_partial_even_divergence(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_scenario_partial_even_divergence(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_scenario_partial_uneven_divergence(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_scenario_partial_uneven_divergence(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_maximal_retention_predicate(self):
        first = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate
                =hstrat.StratumRetentionPredicatePerfectResolution(),
        )
        second = first.Clone()
        third = first.Clone()

        for gen in range(100):
            assert first.GetNumStrataRetained() == gen + 1
            assert second.GetNumStrataRetained() == gen + 1
            assert third.GetNumStrataRetained() == 1

            assert first.CalcRankOfMrcaUncertaintyWith(second) == 0
            assert first.CalcRankOfMrcaUncertaintyWith(third) == 0

            assert first.CalcRanksSinceMrcaUncertaintyWith(second) == 0
            assert second.CalcRanksSinceMrcaUncertaintyWith(first) == 0
            assert first.CalcRanksSinceMrcaUncertaintyWith(third) == 0
            assert third.CalcRanksSinceMrcaUncertaintyWith(first) == 0

            first.DepositStratum()
            second.DepositStratum()
            # no layers deposited onto third

    def test_minimal_retention_predicate(self):
        first = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate
                =hstrat.StratumRetentionPredicateNominalResolution(),
        )
        second = first.Clone()
        third = first.Clone()

        for gen in range(100):
            assert first.GetNumStrataRetained() == min(2, gen+1)
            assert second.GetNumStrataRetained() == min(2, gen+1)
            assert third.GetNumStrataRetained() == 1

            assert (
                first.CalcRankOfMrcaUncertaintyWith(second) == max(0, gen - 1)
            )
            assert first.CalcRankOfMrcaUncertaintyWith(third) == 0

            assert (
                first.CalcRanksSinceMrcaUncertaintyWith(second)
                == max(0, gen - 1)
            )
            assert (
                second.CalcRanksSinceMrcaUncertaintyWith(first)
                == max(0, gen - 1)
            )
            assert first.CalcRanksSinceMrcaUncertaintyWith(third) == 0
            assert third.CalcRanksSinceMrcaUncertaintyWith(first) == 0

            first.DepositStratum()
            second.DepositStratum()
            # no layers deposited onto third

    def test_HasAnyCommonAncestorWith(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_HasAnyCommonAncestorWith(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_DiffRetainedRanks(self):
        for ordered_store in [
            hstrat.HereditaryStratumOrderedStoreDict,
            hstrat.HereditaryStratumOrderedStoreList,
            hstrat.HereditaryStratumOrderedStoreTree,
        ]:
            _do_test_DiffRetainedRanks(
                self,
                ordered_store,
            )

    def test_always_store_rank_in_stratum(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
                hstrat.HereditaryStratumOrderedStoreTree,
            ]:
                _do_test_always_store_rank_in_stratum(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_CalcProbabilityDifferentiaCollision(self):
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        ).CalcProbabilityDifferentiaCollision() == 0.5
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=2,
        ).CalcProbabilityDifferentiaCollision() == 0.25
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=3,
        ).CalcProbabilityDifferentiaCollision() == 0.125
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=8,
        ).CalcProbabilityDifferentiaCollision() == 1.0 / 256.0

    def \
    test_CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
        self
    ):
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.49
        ) == 1
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        ) == 5
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=2,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        ) == 3
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=5,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        ) == 1
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.49
        ) == 1
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        ) == 1
        assert hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.99
        ) == 1

    def test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(self):
        for ordered_store in [
            hstrat.HereditaryStratumOrderedStoreDict,
            hstrat.HereditaryStratumOrderedStoreList,
            hstrat.HereditaryStratumOrderedStoreTree,
        ]:
            _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith2(
                self,
                ordered_store,
            )
            _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith3(
                self,
                ordered_store,
            )
            _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith4(
                self,
                ordered_store,
            )
            _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith5(
                self,
                ordered_store,
            )
            for differentia_width in 1, 2, 8:
                _do_test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith1(
                    self,
                    ordered_store,
                    differentia_width
                )



if __name__ == '__main__':
    unittest.main()
