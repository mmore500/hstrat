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


    def test_comparison_commutativity(self,):

        population = [
            HereditaryStratigraphicColumn()
            for __ in range(10)
        ]

        for generation in range(100):

            for first, second in it.combinations(population, 2):
                # assert commutativity
                assert (
                    first.CalcLastCommonRankWith(second)
                    == second.CalcLastCommonRankWith(first)
                )
                assert (
                    first.CalcFirstDisparateRankWith(second)
                    == second.CalcFirstDisparateRankWith(first)
                )
                assert (
                    first.CalcMrcaRankBoundsWith(second)
                    == second.CalcMrcaRankBoundsWith(first)
                )

            # advance generation
            random.shuffle(population)
            for target in range(5):
                population[target] = deepcopy(population[-1])
            for individual in population: individual.DepositLayer()


    def test_comparison_validity(self,):

        population = [
            HereditaryStratigraphicColumn()
            for __ in range(10)
        ]

        for generation in range(100):

            for first, second in it.combinations(population, 2):
                lcrw = first.CalcLastCommonRankWith(second)
                assert lcrw is None or lcrw <= generation, lcrw

                fdrw = first.CalcFirstDisparateRankWith(second)
                assert fdrw is None or fdrw <= generation, fdrw

                assert first.CalcMrcaRankBoundsWith(second) == (lcrw, fdrw)

            # advance generation
            random.shuffle(population)
            for target in range(5):
                population[target] = deepcopy(population[-1])
            for individual in population: individual.DepositLayer()


    def test_scenario_no_mrca(self,):
        first = HereditaryStratigraphicColumn()
        second = HereditaryStratigraphicColumn()

        for generation in range(100):

            assert first.CalcLastCommonRankWith(second) == None
            assert second.CalcLastCommonRankWith(first) == None

            assert first.CalcFirstDisparateRankWith(second) == 0
            assert second.CalcFirstDisparateRankWith(first) == 0

            first.DepositLayer()
            second.DepositLayer()


    def test_scenario_no_divergence(self,):
        first = HereditaryStratigraphicColumn()

        for generation in range(100):

            assert first.CalcLastCommonRankWith(first) == generation

            assert first.CalcFirstDisparateRankWith(first) == None

            first.DepositLayer()


if __name__ == '__main__':
    unittest.main()
