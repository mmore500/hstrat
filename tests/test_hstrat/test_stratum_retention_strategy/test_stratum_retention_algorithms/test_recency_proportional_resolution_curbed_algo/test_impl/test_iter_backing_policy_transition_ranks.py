import interval_search as inch
import pytest

import hstrat._auxiliary_lib as auxlib
from hstrat.stratum_retention_strategy.stratum_retention_algorithms.recency_proportional_resolution_curbed_algo._impl import (
    calc_geom_seq_nth_root_transition_rank,
    calc_provided_resolution,
)

from ..impl import iter_backing_policy_transition_ranks


@pytest.mark.parametrize(
    "size_curb",
    reversed(range(1, 1024)),
)
def test_iter_backing_policy_transition_ranks(size_curb):

    *test_ranks, gsnra_rank = [
        0,
        *iter_backing_policy_transition_ranks(size_curb),
    ]

    assert sorted(test_ranks) == test_ranks
    assert len(set(test_ranks)) == len(test_ranks)

    assert gsnra_rank == calc_geom_seq_nth_root_transition_rank(size_curb), (
        gsnra_rank,
        test_ranks[-1],
    )

    for tr1, tr2 in auxlib.pairwise(test_ranks[int(size_curb == 1) : -1]):
        assert tr1 < tr2
        assert tr1 == 0 or calc_provided_resolution(
            size_curb, tr1 - 1
        ) > calc_provided_resolution(size_curb, tr1)
        assert calc_provided_resolution(
            size_curb, tr2 - 1
        ) > calc_provided_resolution(size_curb, tr2)

        assert calc_provided_resolution(
            size_curb, tr1
        ) > calc_provided_resolution(size_curb, tr2)
        assert calc_provided_resolution(
            size_curb, tr1
        ) == calc_provided_resolution(size_curb, tr2 - 1)

    assert (
        len(test_ranks) == 0
        or test_ranks[-1] == 0
        or calc_provided_resolution(size_curb, test_ranks[-1]) >= 0
    )

    assert (
        gsnra_rank == 0
        or calc_provided_resolution(size_curb, gsnra_rank - 1) >= 0
    )
    assert calc_provided_resolution(size_curb, gsnra_rank + 1) < 0
    assert calc_provided_resolution(size_curb, gsnra_rank) < 0


def _iter_backing_policy_transition_ranks_naive(size_curb):
    gsnra_rank = calc_geom_seq_nth_root_transition_rank(size_curb)

    cur_rank = 0
    while cur_rank < gsnra_rank:
        cur_resolution = calc_provided_resolution(size_curb, cur_rank)
        cur_rank = inch.binary_search(
            lambda r: calc_provided_resolution(size_curb, r) != cur_resolution,
            cur_rank,
            gsnra_rank,
        )
        yield cur_rank


@pytest.mark.parametrize(
    "size_curb",
    reversed(range(1, 1024)),
)
def test_iter_backing_policy_transition_ranks_naive(size_curb):
    assert [*iter_backing_policy_transition_ranks(size_curb)] == [
        *_iter_backing_policy_transition_ranks_naive(size_curb)
    ]
