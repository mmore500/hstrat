import itertools as it

import numpy as np
import pytest

from hstrat.hstrat import recency_proportional_resolution_algo as rpra


@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "num_stratum_depositions_completed",
    it.chain(
        map(
            int,
            np.random.default_rng(1).integers(
                2**63,
                size=20,
            ),
        ),
        range(100),
        range(0, 10000, 1007),
    ),
)
def test_impl_consistency(
    recency_proportional_resolution: int,
    num_stratum_depositions_completed: int,
):
    assert len(
        {
            impl(
                recency_proportional_resolution,
                num_stratum_depositions_completed,
            )
            for impl in rpra._impl._num_to_condemn_.impls
        }
    )
