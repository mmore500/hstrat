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
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        hstrat.col_to_specimen,
    ],
)
def test_DiffRetainedRanks(ordered_store, wrap):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
    )
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )

    assert hstrat.diff_retained_ranks(wrap(first), wrap(second)) == (
        set(),
        set(),
    )
    assert hstrat.diff_retained_ranks(wrap(second), wrap(first)) == (
        set(),
        set(),
    )

    first.DepositStratum()
    assert hstrat.diff_retained_ranks(wrap(first), wrap(second)) == (
        {1},
        set(),
    )
    assert hstrat.diff_retained_ranks(wrap(second), wrap(first)) == (
        set(),
        {1},
    )

    second.DepositStratum()
    assert hstrat.diff_retained_ranks(wrap(first), wrap(second)) == (
        set(),
        set(),
    )
    assert hstrat.diff_retained_ranks(wrap(second), wrap(first)) == (
        set(),
        set(),
    )

    first.DepositStratum()
    assert hstrat.diff_retained_ranks(wrap(first), wrap(second)) == ({2}, {1})
    assert hstrat.diff_retained_ranks(wrap(second), wrap(first)) == ({1}, {2})

    second.DepositStratum()
    assert hstrat.diff_retained_ranks(wrap(first), wrap(second)) == (
        set(),
        {1},
    )
    assert hstrat.diff_retained_ranks(wrap(second), wrap(first)) == (
        {1},
        set(),
    )
