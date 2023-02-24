import itertools as it

import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import (
    is_strictly_increasing,
    random_choice_generator,
)


@pytest.mark.parametrize(
    "differentia_bit_width", [1, 2, 7, 8, 16, 32, 64, 129]
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=2
        ),
    ],
)
@pytest.mark.parametrize("synchronous_generations", [True, False])
@pytest.mark.parametrize("population_size", [1, 2, 9])
@pytest.mark.parametrize("num_generations", [0, 1, 257])
def test_init_and_getters(
    differentia_bit_width,
    retention_policy,
    synchronous_generations,
    population_size,
    num_generations,
):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_bit_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(population_size)
    ]
    reproduction_queue = (
        it.cycle if synchronous_generations else random_choice_generator
    )(population)
    for selection in it.islice(
        reproduction_queue, 0, num_generations * population_size
    ):
        selection.DepositStratum()

    assemblage = hstrat.pop_to_assemblage(population)

    for specimen, column in zip(assemblage.BuildSpecimens(), population):
        assert (
            specimen.GetNumStrataDeposited() == column.GetNumStrataDeposited()
        )
        assert (
            specimen.GetStratumDifferentiaBitWidth()
            == column.GetStratumDifferentiaBitWidth()
        )
        assert specimen.GetNumStrataRetained() == column.GetNumStrataRetained()
        assert {*specimen.GetDifferentiaVals()} >= {
            *column.IterRetainedDifferentia()
        }
        assert [
            *specimen.GetDifferentiaVals()[~specimen.GetStratumMask()]
        ] >= [*column.IterRetainedDifferentia()]
        assert {*specimen.GetRankIndex()} >= {*column.IterRetainedRanks()}
        assert [*specimen.GetRankIndex()[~specimen.GetStratumMask()]] == [
            *column.IterRetainedRanks()
        ]
        assert is_strictly_increasing(specimen.GetRankIndex())

        assert [*specimen.GetData().dropna()] == [
            *column.IterRetainedDifferentia()
        ]
        assert {*specimen.GetData().index} >= {*column.IterRetainedRanks()}
        assert is_strictly_increasing(specimen.GetData().index)

        for index in range(column.GetNumStrataRetained()):
            assert specimen.GetRankAtColumnIndex(
                index
            ) == column.GetRankAtColumnIndex(index)

        assert [*specimen.IterRetainedRanks()] == [*column.IterRetainedRanks()]
        assert [*specimen.IterRetainedDifferentia()] == [
            *column.IterRetainedDifferentia()
        ]

        assert (
            specimen.GetNumDiscardedStrata() == column.GetNumDiscardedStrata()
        )
        assert specimen.HasDiscardedStrata() == column.HasDiscardedStrata()
