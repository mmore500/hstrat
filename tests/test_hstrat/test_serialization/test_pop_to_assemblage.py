import functools
import operator

import pytest
from tqdm import tqdm

from hstrat import hstrat


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=4
        ),
    ],
)
@pytest.mark.parametrize(
    "num_deposits",
    [0, 1, 6, 8, 13],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 20, 32, 64],
)
@pytest.mark.parametrize(
    "pop_size",
    [0, 1, 2, 8, 13],
)
def test_pop_to_assemblage(
    retention_policy,
    num_deposits,
    differentia_bit_width,
    pop_size,
):
    pop = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
            stratum_differentia_bit_width=differentia_bit_width,
        ).CloneNthDescendant(num_deposits)
        for __ in range(pop_size)
    ]

    hsa = hstrat.pop_to_assemblage(
        pop, progress_wrap=functools.partial(tqdm, disable=True)
    )
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(
                col.IterRetainedRanks(),
                assemblage_specimen.GetData().notna().index,
            ),
        )
        for col, assemblage_specimen in zip(pop, hsa.BuildSpecimens())
    )
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(
                col.IterRetainedDifferentia(),
                assemblage_specimen.GetData().notna(),
            ),
        )
        for col, assemblage_specimen in zip(pop, hsa.BuildSpecimens())
    )
