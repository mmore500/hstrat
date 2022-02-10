#!/bin/python3

from copy import deepcopy
import itertools as it
import random
import unittest

from pylib import HereditaryStratigraphicColumn

random.seed(1)

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

        population = [
            HereditaryStratigraphicColumn()
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


    def test_comparison_commutativity_syncrhonous(self,):

        population = [
            HereditaryStratigraphicColumn()
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


    def test_comparison_validity(self,):

        population = [
            HereditaryStratigraphicColumn()
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


    def test_scenario_no_mrca(self,):
        first = HereditaryStratigraphicColumn()
        second = HereditaryStratigraphicColumn()

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


    def test_scenario_no_divergence(self,):
        first = HereditaryStratigraphicColumn()

        for generation in range(100):

            assert first.CalcRankOfLastCommonalityWith(first) == generation

            assert first.CalcRankOfFirstDisparityWith(first) == None

            assert first.CalcRanksSinceLastCommonalityWith(first) == 0

            assert first.CalcRanksSinceFirstDisparityWith(first) == None

            first.DepositLayer()


    def test_scenario_partial_even_divergence(self,):
        first = HereditaryStratigraphicColumn()

        for generation in range(100):
            first.DepositLayer()

        second = deepcopy(first)

        first.DepositLayer()
        second.DepositLayer()

        for generation in range(101, 200):

            assert (
                0
                < first.CalcRankOfLastCommonalityWith(second)
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


    def test_scenario_partial_uneven_divergence(self,):
        first = HereditaryStratigraphicColumn()

        for generation in range(100):
            first.DepositLayer()

        second = deepcopy(first)

        first.DepositLayer()

        for generation in range(101, 200):

            assert (
                0
                < first.CalcRankOfLastCommonalityWith(second)
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
                < first.CalcRankOfLastCommonalityWith(second)
                <= 100
            )
            assert (
                100
                <= first.CalcRankOfFirstDisparityWith(second)
                <= generation
            )


            assert (
                100
                <= first.CalcRanksSinceLastCommonalityWith(second)
                <= 200
            )
            assert (
                0
                < second.CalcRanksSinceLastCommonalityWith(first)
                <= generation - 100
            )
            assert (
                0
                <= first.CalcRanksSinceFirstDisparityWith(second)
                < 100
            )
            assert (
                0
                <= second.CalcRanksSinceFirstDisparityWith(first)
                < generation - 100
            )

            second.DepositLayer()

    def test_maximal_retention_predicate(self,):
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=lambda **kwargs: True,
        )

        for gen in range(100):
            assert column.GetColumnSize() == gen + 1
            column.DepositLayer()


    def test_minimal_retention_predicate(self,):
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate
                =lambda *, column_layers_deposited, stratum_rank: (
                stratum_rank in (0, column_layers_deposited - 1,)
            ),
        )

        for gen in range(100):
            assert 1 <= column.GetColumnSize() <= 2
            column.DepositLayer()


if __name__ == '__main__':
    unittest.main()
