import functools
import json
import logging
import operator

import pytest
from tqdm import tqdm

from hstrat import genome_instrumentation, hstrat
from hstrat._auxiliary_lib import get_hstrat_version, log_once_in_a_row


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
        ).CloneNthDescendant(num_deposits)
        for __ in range(pop_size)
    ]

    hsa = hstrat.pop_to_assemblage(
        pop, progress_wrap=functools.partial(tqdm, disable=True)
    )
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(col.IterRetainedRanks(), assemblage_specimen.notna().index),
        )
        for col, assemblage_specimen in zip(pop, hsa.IterSpecimens())
    )
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(col.IterRetainedDifferentia(), assemblage_specimen.notna()),
        )
        for col, assemblage_specimen in zip(pop, hsa.IterSpecimens())
    )
