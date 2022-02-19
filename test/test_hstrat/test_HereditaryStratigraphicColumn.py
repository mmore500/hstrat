from copy import deepcopy
from iterpop import iterpop as ip
import itertools as it
import random
import unittest

from pylib import helpers
from pylib import hstrat

random.seed(1)


def _do_test_equality(
    testcase,
    retention_predicate,
    ordered_store
):

    original1 = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_predicate=retention_predicate,
    )
    copy1 = deepcopy(original1)
    original2 = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_predicate=retention_predicate,
    )

    assert original1 == copy1
    assert original1 != original2
    assert copy1 != original2

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
                first.CalcRankOfLastCommonalityWith(second)
                == second.CalcRankOfLastCommonalityWith(first)
            )
            assert (
                first.CalcRankOfFirstDisparityWith(second)
                == second.CalcRankOfFirstDisparityWith(first)
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
            population[target] = population[-1].MakeDescendantColumn()
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
        deepcopy(column)
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
            population[target] = deepcopy(population[-1])
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
                    =hstrat.StratumRetentionCondemnerMaximal(),
            ),
        })

    column = make_bundle()
    frozen_copy = deepcopy(column)
    frozen_unrelated = make_bundle()
    population = [
        deepcopy(column)
        for __ in range(10)
    ]
    forked_isolated = deepcopy(column)
    unrelated_isolated = make_bundle()

    for generation in range(100):

        for f, s in it.chain(
            it.combinations(population, 2),
            zip(population, helpers.cyclify(forked_isolated)),
            zip(population, helpers.cyclify(frozen_copy)),
            zip(helpers.cyclify(forked_isolated), population),
            zip(helpers.cyclify(frozen_copy), population),
        ):
            lb, ub = f['test'].CalcRankOfMrcaBoundsWith(s['test'])
            actual_rank_of_mrca = f['control'].GetLastCommonStratumWith(
                s['control'],
            ).GetAnnotation()
            assert lb <= actual_rank_of_mrca < ub

        for f, s in it.chain(
            zip(population, helpers.cyclify(frozen_unrelated)),
            zip(population, helpers.cyclify(unrelated_isolated)),
            zip(helpers.cyclify(frozen_unrelated), population),
            zip(helpers.cyclify(unrelated_isolated), population),
        ):
            assert f['test'].CalcRankOfMrcaBoundsWith(s['test']) is None

        # advance generation
        random.shuffle(population)
        for target in range(3):
            population[target] = population[-1].MakeDescendantColumn(
                stratum_annotation=population[-1].GetNumStrataDeposited(),
            )
        for individual in it.chain(
            iter(population),
            helpers.iterify(forked_isolated),
            helpers.iterify(unrelated_isolated),
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
                    =hstrat.StratumRetentionCondemnerMaximal(),
            ),
        })

    column = make_bundle()
    frozen_copy = deepcopy(column)
    frozen_unrelated = make_bundle()
    population = [
        deepcopy(column)
        for __ in range(10)
    ]
    forked_isolated = deepcopy(column)
    unrelated_isolated = make_bundle()

    for generation in range(100):

        for f, s in it.chain(
            it.combinations(population, 2),
            zip(population, helpers.cyclify(forked_isolated)),
            zip(population, helpers.cyclify(frozen_copy)),
            zip(helpers.cyclify(forked_isolated), population),
            zip(helpers.cyclify(frozen_copy), population),
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
            zip(population, helpers.cyclify(frozen_unrelated)),
            zip(population, helpers.cyclify(unrelated_isolated)),
            zip(helpers.cyclify(frozen_unrelated), population),
            zip(helpers.cyclify(unrelated_isolated), population),
        ):
            assert f['test'].CalcRanksSinceMrcaBoundsWith(s['test']) is None

        # advance generation
        random.shuffle(population)
        for target in range(3):
            population[target] = deepcopy(population[-1])
            population[target].DepositStratum(
                annotation=population[target].GetNumStrataDeposited(),
            )
        for individual in it.chain(
            iter(population),
            helpers.iterify(forked_isolated),
            helpers.iterify(unrelated_isolated),
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
                first.CalcRankOfLastCommonalityWith(second)
                == second.CalcRankOfLastCommonalityWith(first)
            )
            assert (
                first.CalcRankOfFirstDisparityWith(second)
                == second.CalcRankOfFirstDisparityWith(first)
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
                first.CalcRanksSinceLastCommonalityWith(second)
                == second.CalcRanksSinceLastCommonalityWith(first)
            )
            assert (
                first.CalcRanksSinceFirstDisparityWith(second)
                == second.CalcRanksSinceFirstDisparityWith(first)
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
            population[target] = deepcopy(population[-1])
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
            lcrw = first.CalcRankOfLastCommonalityWith(second)
            if lcrw is not None:
                assert 0 <= lcrw <= generation

            fdrw = first.CalcRankOfFirstDisparityWith(second)
            if fdrw is not None:
                assert 0 <= fdrw <= generation

            assert (
                first.CalcRankOfMrcaBoundsWith(second)
                in [
                    (
                        lcrw,
                        helpers.value_or(fdrw, first.GetNumStrataDeposited())
                    ),
                    None,
                ]
            )
            if lcrw is not None and fdrw is not None:
                assert lcrw < fdrw

            assert first.CalcRankOfMrcaUncertaintyWith(second) >= 0

            rslcw = first.CalcRanksSinceLastCommonalityWith(second)
            if rslcw is not None:
                assert 0 <= rslcw <= generation

            rsfdw = first.CalcRanksSinceFirstDisparityWith(second)
            if rsfdw is not None:
                assert -1 <= rsfdw <= generation

            assert (
                first.CalcRanksSinceMrcaBoundsWith(second) is None
                or first.CalcRanksSinceMrcaBoundsWith(second)
                    == (helpers.value_or(rsfdw, -1) + 1, rslcw + 1)
            )
            if rslcw is not None and rsfdw is not None:
                assert rsfdw < rslcw

            assert first.CalcRanksSinceMrcaUncertaintyWith(second) >= 0

        # advance generations asynchronously
        random.shuffle(population)
        for target in range(5):
            population[target] = deepcopy(population[-1])
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
        assert first.CalcRankOfLastCommonalityWith(second) == None
        assert second.CalcRankOfLastCommonalityWith(first) == None

        assert first.CalcRankOfFirstDisparityWith(second) == 0
        assert second.CalcRankOfFirstDisparityWith(first) == 0

        assert first.CalcRankOfMrcaUncertaintyWith(second) == 0
        assert second.CalcRankOfMrcaUncertaintyWith(first) == 0

        assert first.CalcRanksSinceLastCommonalityWith(second) == None
        assert second.CalcRanksSinceLastCommonalityWith(first) == None

        assert first.CalcRanksSinceFirstDisparityWith(second) == generation
        assert second.CalcRanksSinceFirstDisparityWith(first) == generation

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

        assert column.CalcRankOfLastCommonalityWith(column) == generation
        assert column.CalcRankOfFirstDisparityWith(column) == None
        assert column.CalcRankOfMrcaUncertaintyWith(column) == 0

        assert column.CalcRanksSinceLastCommonalityWith(column) == 0
        assert column.CalcRanksSinceFirstDisparityWith(column) == None
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

    second = deepcopy(first)

    first.DepositStratum()
    second.DepositStratum()

    for generation in range(101, 200):
        assert (
            0
            <= first.CalcRankOfLastCommonalityWith(second)
            <= 100
        )
        assert (
            100
            <= first.CalcRankOfFirstDisparityWith(second)
            <= generation
        )
        assert (
            generation - 101
            < first.CalcRanksSinceLastCommonalityWith(second)
            <= generation
        )
        assert (
            0
            <= first.CalcRanksSinceFirstDisparityWith(second)
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

    second = deepcopy(first)

    first.DepositStratum()

    for generation in range(101, 200):
        assert (
            0
            <= first.CalcRankOfLastCommonalityWith(second)
            <= 100
        )
        assert (
            100
            <= first.CalcRankOfFirstDisparityWith(second)
            <= generation
        )

        assert (
            generation - 101
            < first.CalcRanksSinceLastCommonalityWith(second)
            <= generation
        )
        assert (
            0
            <= second.CalcRanksSinceLastCommonalityWith(first)
            <= 100
        )
        assert (
            0
            <= first.CalcRanksSinceFirstDisparityWith(second)
            < generation - 100
        )
        assert (
            -1 == second.CalcRanksSinceFirstDisparityWith(first)
        )

        first.DepositStratum()

    second.DepositStratum()

    for generation in range(101, 200):
        assert (
            0
            <= first.CalcRankOfLastCommonalityWith(second)
            <= 100
        )
        assert (
            100
            <= first.CalcRankOfFirstDisparityWith(second)
            <= generation + 1
        )

        assert (
            100
            <= first.CalcRanksSinceLastCommonalityWith(second)
            <= 200
        )
        assert (
            0
            <= second.CalcRanksSinceLastCommonalityWith(first)
            <= generation
        )
        assert (
            0
            <= first.CalcRanksSinceFirstDisparityWith(second)
            < 100
        )
        assert (
            -1
            <= second.CalcRanksSinceFirstDisparityWith(first)
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
    first_copy = deepcopy(first)
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


class TestHereditaryStratigraphicColumn(unittest.TestCase):

    def test_GetNumStrataDeposited(self):
        column = hstrat.HereditaryStratigraphicColumn()
        for i in range(10):
            assert column.GetNumStrataDeposited() == i + 1
            column.DepositStratum()

    def test_MakeDescendantColumn(self):
        column = hstrat.HereditaryStratigraphicColumn()
        assert column.GetNumStrataDeposited() == 1
        descendant = column.MakeDescendantColumn(
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

    def test_equality(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_equality(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_comparison_commutativity_asyncrhonous(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_comparison_commutativity_asyncrhonous(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_annotation(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_annotation(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_CalcRankOfMrcaBoundsWith(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_CalcRankOfMrcaBoundsWith(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_CalcRanksSinceMrcaBoundsWith(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_CalcRanksSinceMrcaBoundsWith(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_comparison_commutativity_syncrhonous(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_comparison_commutativity_syncrhonous(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_comparison_validity(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_comparison_validity(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_scenario_no_mrca(self):
        for rp1, rp2 in it.product(
            [
                hstrat.StratumRetentionPredicateMaximal(),
                hstrat.StratumRetentionPredicateMinimal(),
                hstrat.StratumRetentionPredicateDepthProportionalResolution(),
                hstrat.StratumRetentionPredicateFixedResolution(),
                hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
                hstrat.StratumRetentionPredicateRecursiveInterspersion(),
                hstrat.StratumRetentionPredicateStochastic(),
            ],
            repeat=2,
        ):
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_scenario_no_mrca(
                    self,
                    rp1,
                    rp2,
                    ordered_store,
                )

    def test_scenario_no_divergence(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_scenario_no_divergence(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_scenario_partial_even_divergence(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_scenario_partial_even_divergence(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_scenario_partial_uneven_divergence(self):
        for retention_predicate in [
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_scenario_partial_uneven_divergence(
                    self,
                    retention_predicate,
                    ordered_store,
                )

    def test_maximal_retention_predicate(self):
        first = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=hstrat.StratumRetentionPredicateMaximal(),
        )
        second = deepcopy(first)
        third = deepcopy(first)

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
            stratum_retention_predicate=hstrat.StratumRetentionPredicateMinimal(),
        )
        second = deepcopy(first)
        third = deepcopy(first)

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
            hstrat.StratumRetentionPredicateMaximal(),
            hstrat.StratumRetentionPredicateMinimal(),
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateRecursiveInterspersion(),
            hstrat.StratumRetentionPredicateStochastic(),
        ]:
            for ordered_store in [
                hstrat.HereditaryStratumOrderedStoreDict,
                hstrat.HereditaryStratumOrderedStoreList,
            ]:
                _do_test_HasAnyCommonAncestorWith(
                    self,
                    retention_predicate,
                    ordered_store,
                )


if __name__ == '__main__':
    unittest.main()
