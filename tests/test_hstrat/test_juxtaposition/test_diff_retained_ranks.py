import itertools as it

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


@pytest.mark.parametrize(
    "differentia_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(3),
        hstrat.recency_proportional_resolution_algo.Policy(1),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.perfect_resolution_algo.Policy(),
    ],
)
def test_artifact_types_equiv(differentia_width, policy):
    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_width,
    ).CloneNthDescendant(7)
    c1 = common_ancestor.CloneNthDescendant(4)
    c2 = common_ancestor.CloneNthDescendant(9)
    c_x = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_width,
    ).CloneNthDescendant(7)
    c_y = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_width,
    )

    for a, b in it.product(
        [common_ancestor, c1, c2, c_x, c_y],
        [common_ancestor, c1, c2, c_x, c_y],
    ):
        assert hstrat.diff_retained_ranks(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
        ) == hstrat.diff_retained_ranks(a, b)
