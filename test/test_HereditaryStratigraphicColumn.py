#!/bin/python3

from copy import deepcopy
import itertools as it
import random
import unittest

from pylib import HereditaryStratigraphicColumn
from pylib import stratum_retention_predicate_maximal
from pylib import stratum_retention_predicate_minimal

random.seed(1)

def _do_test_comparison_commutativity_asyncrhonous(
    testcase,
    retention_predicate,
):

    population = [
        HereditaryStratigraphicColumn(
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

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = deepcopy(population[-1])
        for individual in population:
            # asynchronous generations
            if random.choice([True, False]):
                individual.DepositLayer()


def _do_test_comparison_commutativity_syncrhonous(
    testcase,
    retention_predicate,
):

    population = [
            HereditaryStratigraphicColumn(
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

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = deepcopy(population[-1])
        # synchronous generations
        for individual in population: individual.DepositLayer()


def _do_test_comparison_validity(
    testcase,
    retention_predicate,
):

    population = [
        HereditaryStratigraphicColumn(
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

            assert first.CalcRankOfMrcaBoundsWith(second) == (lcrw, fdrw)
            if lcrw is not None and fdrw is not None:
                assert lcrw < fdrw

            rslcw = first.CalcRanksSinceLastCommonalityWith(second)
            if rslcw is not None:
                assert 0 <= rslcw <= generation

            rsfdw = first.CalcRanksSinceFirstDisparityWith(second)
            if rsfdw is not None:
                assert -1 <= rsfdw <= generation

            assert (
                first.CalcRanksSinceMrcaBoundsWith(second) == (rslcw, rsfdw)
            )
            if rslcw is not None and rsfdw is not None:
                assert rslcw > rsfdw

        # advance generations asynchronously
        random.shuffle(population)
        for target in range(5):
            population[target] = deepcopy(population[-1])
        for individual in population:
            if random.choice([True, False]):
                individual.DepositLayer()


def _do_test_scenario_no_mrca(
    testcase,
    retention_predicate1,
    retention_predicate2,
):
    first = HereditaryStratigraphicColumn(
        stratum_retention_predicate=retention_predicate1,
    )
    second = HereditaryStratigraphicColumn(
        stratum_retention_predicate=retention_predicate2,
    )

    for generation in range(100):

        assert first.CalcRankOfLastCommonalityWith(second) == None
        assert second.CalcRankOfLastCommonalityWith(first) == None

        assert first.CalcRankOfFirstDisparityWith(second) == 0
        assert second.CalcRankOfFirstDisparityWith(first) == 0

        assert first.CalcRanksSinceLastCommonalityWith(second) == None
        assert second.CalcRanksSinceLastCommonalityWith(first) == None

        assert first.CalcRanksSinceFirstDisparityWith(second) == generation
        assert second.CalcRanksSinceFirstDisparityWith(first) == generation

        first.DepositLayer()
        second.DepositLayer()


def _do_test_scenario_no_divergence(
    testcase,
    retention_predicate,
):
    column = HereditaryStratigraphicColumn(
        stratum_retention_predicate=retention_predicate,
    )

    for generation in range(100):

        assert column.CalcRankOfLastCommonalityWith(column) == generation

        assert column.CalcRankOfFirstDisparityWith(column) == None

        assert column.CalcRanksSinceLastCommonalityWith(column) == 0

        assert column.CalcRanksSinceFirstDisparityWith(column) == None

        column.DepositLayer()


def _do_test_scenario_partial_even_divergence(
    testcase,
    retention_predicate,
):
    first = HereditaryStratigraphicColumn(
        stratum_retention_predicate=retention_predicate,
    )

    for generation in range(100):
        first.DepositLayer()

    second = deepcopy(first)

    first.DepositLayer()
    second.DepositLayer()

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

        first.DepositLayer()
        second.DepositLayer()


def _do_test_scenario_partial_uneven_divergence(
    self,
    retention_predicate,
):
    first = HereditaryStratigraphicColumn(
        stratum_retention_predicate=retention_predicate,
    )

    for generation in range(100):
        first.DepositLayer()

    second = deepcopy(first)

    first.DepositLayer()

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


        first.DepositLayer()

    second.DepositLayer()

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

        second.DepositLayer()


class TestHereditaryStratigraphicColumn(unittest.TestCase):

    def test_GetNumLayersDeposited(self,):

        column = HereditaryStratigraphicColumn()
        for i in range(10):
            assert column.GetNumLayersDeposited() == i + 1
            column.DepositLayer()


    def test_equality(self,):

        original1 = HereditaryStratigraphicColumn()
        copy1 = deepcopy(original1,)
        original2 = HereditaryStratigraphicColumn()

        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

        copy1.DepositLayer()
        assert original1 != copy1

        original1.DepositLayer()
        assert original1 != copy1


    def test_comparison_commutativity_asyncrhonous(self,):
        for retention_predicate in [
            stratum_retention_predicate_maximal,
            stratum_retention_predicate_minimal,
        ]:
            _do_test_comparison_commutativity_asyncrhonous(
                self,
                retention_predicate,
            )

    def test_comparison_commutativity_syncrhonous(self,):
        for retention_predicate in [
            stratum_retention_predicate_maximal,
            stratum_retention_predicate_minimal,
        ]:
            _do_test_comparison_commutativity_syncrhonous(
                self,
                retention_predicate,
            )


    def test_comparison_validity(self,):
        for retention_predicate in [
            stratum_retention_predicate_maximal,
            stratum_retention_predicate_minimal,
        ]:
            _do_test_comparison_validity(
                self,
                retention_predicate,
            )


    def test_scenario_no_mrca(self,):
        for rp1, rp2 in it.product(
            [
                stratum_retention_predicate_maximal,
                stratum_retention_predicate_minimal,
            ],
            repeat=2,
        ):
            _do_test_scenario_no_mrca(
                self,
                rp1,
                rp2,
            )


    def test_scenario_no_divergence(self,):
        for retention_predicate in [
            stratum_retention_predicate_maximal,
            stratum_retention_predicate_minimal,
        ]:
            _do_test_scenario_no_divergence(
                self,
                retention_predicate,
            )


    def test_scenario_partial_even_divergence(self,):
        for retention_predicate in [
            stratum_retention_predicate_maximal,
            stratum_retention_predicate_minimal,
        ]:
            _do_test_scenario_partial_even_divergence(
                self,
                retention_predicate,
            )


    def test_scenario_partial_uneven_divergence(self,):
        for retention_predicate in [
            stratum_retention_predicate_maximal,
            stratum_retention_predicate_minimal,
        ]:
            _do_test_scenario_partial_uneven_divergence(
                self,
                retention_predicate,
            )


    def test_maximal_retention_predicate(self,):
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=stratum_retention_predicate_maximal,
        )

        for gen in range(100):
            assert column.GetColumnSize() == gen + 1
            column.DepositLayer()


    def test_minimal_retention_predicate(self,):
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=stratum_retention_predicate_minimal,
        )

        for gen in range(100):
            assert 1 <= column.GetColumnSize() <= 2
            column.DepositLayer()


if __name__ == '__main__':
    unittest.main()
