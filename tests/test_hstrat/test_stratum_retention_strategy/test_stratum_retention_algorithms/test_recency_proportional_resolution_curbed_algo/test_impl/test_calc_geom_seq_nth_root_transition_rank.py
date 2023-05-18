import pytest

from hstrat.stratum_retention_strategy.stratum_retention_algorithms.recency_proportional_resolution_curbed_algo._impl import (
    calc_geom_seq_nth_root_transition_rank,
    calc_provided_resolution,
)


@pytest.mark.parametrize(
    "size_curb",
    reversed(range(1, 1024)),
)
def test_calc_provided_resolution_consistency(size_curb):
    transition_rank = calc_geom_seq_nth_root_transition_rank(size_curb)

    if transition_rank:
        assert calc_provided_resolution(size_curb, transition_rank - 1) >= 0
    assert calc_provided_resolution(size_curb, transition_rank) < 0
