import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_DiffRetainedRanks(ordered_store):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
    )
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )

    assert hstrat.diff_retained_ranks(first, second) == (set(), set())
    assert hstrat.diff_retained_ranks(second, first) == (set(), set())

    first.DepositStratum()
    assert hstrat.diff_retained_ranks(first, second) == ({1}, set())
    assert hstrat.diff_retained_ranks(second, first) == (set(), {1})

    second.DepositStratum()
    assert hstrat.diff_retained_ranks(first, second) == (set(), set())
    assert hstrat.diff_retained_ranks(second, first) == (set(), set())

    first.DepositStratum()
    assert hstrat.diff_retained_ranks(first, second) == ({2}, {1})
    assert hstrat.diff_retained_ranks(second, first) == ({1}, {2})

    second.DepositStratum()
    assert hstrat.diff_retained_ranks(first, second) == (set(), {1})
    assert hstrat.diff_retained_ranks(second, first) == ({1}, set())
