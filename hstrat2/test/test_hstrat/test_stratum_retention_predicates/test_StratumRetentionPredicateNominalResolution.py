from copy import deepcopy
import random
import unittest

random.seed(1)

from hstrat import hstrat


class TestStratumRetentionPredicateNominalResolution(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        assert (
            hstrat.StratumRetentionPredicateNominalResolution()
            == hstrat.StratumRetentionPredicateNominalResolution()
        )

        original = hstrat.StratumRetentionPredicateNominalResolution()
        copy = deepcopy(original)
        assert original == copy

    def test_behavior(self):
        for num_stratum_depositions_completed in range(100):
            for stratum_rank in range(0, num_stratum_depositions_completed):
                assert not hstrat.StratumRetentionPredicateNominalResolution()(
                    num_stratum_depositions_completed
                    =num_stratum_depositions_completed,
                    stratum_rank=stratum_rank,
                ) or stratum_rank in (0, num_stratum_depositions_completed)

    def test_space_complexity(self):
        predicate = hstrat.StratumRetentionPredicateNominalResolution()
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        for column_strata_deposited in range(100):
            for stratum_rank in range(0, column_strata_deposited):
                upper_bound = predicate.CalcNumStrataRetainedUpperBound(
                    num_strata_deposited=column.GetNumStrataDeposited(),
                )
                assert column.GetNumStrataRetained() <= upper_bound

    def _do_test_resolution(self, synchronous):
        predicate = hstrat.StratumRetentionPredicateNominalResolution()
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        population = [
            column.Clone()
            for __ in range(25)
        ]

        for generation in range(500):
            # subsample consecutive pairs in population
            for f, s in  zip(population, population[1:]):
                target_resolu = predicate.CalcMrcaUncertaintyUpperBound(
                    first_num_strata_deposited=f.GetNumStrataDeposited(),
                    second_num_strata_deposited=s.GetNumStrataDeposited(),
                )
                assert f.CalcRankOfMrcaUncertaintyWith(s) <= target_resolu
                assert f.CalcRanksSinceMrcaUncertaintyWith(s) <= target_resolu

            random.shuffle(population)
            for target in range(5):
                population[target] = population[-1].Clone()
            for individual in population:
                if synchronous or random.choice([True, False]):
                    individual.DepositStratum()

    def test_resolution(self):
        for synchronous in [True, False]:
            self._do_test_resolution(synchronous)

    def test_CalcRankAtColumnIndex(self):
        predicate = hstrat.StratumRetentionPredicateNominalResolution()
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
            initial_stratum_annotation=0,
        )

        for generation in range(1,501):
            for index in range(column.GetNumStrataRetained()):
                assert (
                    column.GetStratumAtColumnIndex(index).GetAnnotation()
                    == column.GetRankAtColumnIndex(index)
                )
            column.DepositStratum(annotation=generation)


if __name__ == '__main__':
    unittest.main()
