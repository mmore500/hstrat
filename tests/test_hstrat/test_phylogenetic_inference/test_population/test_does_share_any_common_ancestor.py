import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_does_share_any_common_ancestor(retention_policy, ordered_store):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    first_copy = first.Clone()
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    def assert_validity():
        wrap = hstrat.col_to_specimen
        assert hstrat.does_share_any_common_ancestor(
            [wrap(first), wrap(first), wrap(first)]
        )
        assert hstrat.does_share_any_common_ancestor([first, first, first])
        assert hstrat.does_share_any_common_ancestor(
            [first_copy, first_copy, first_copy]
        )
        assert hstrat.does_share_any_common_ancestor(
            [first, first_copy, first]
        )
        assert hstrat.does_share_any_common_ancestor(
            [first_copy, first, first]
        )
        assert hstrat.does_share_any_common_ancestor(
            [first_copy, first, first] * 3
        )

        assert not hstrat.does_share_any_common_ancestor(
            [second, first, first]
        )
        assert not hstrat.does_share_any_common_ancestor(
            [first, second, first]
        )
        assert not hstrat.does_share_any_common_ancestor(
            [second, first_copy, first]
        )
        assert not hstrat.does_share_any_common_ancestor(
            [first_copy, second, first]
        )
        assert not hstrat.does_share_any_common_ancestor(
            [second, first, second]
        )
        assert not hstrat.does_share_any_common_ancestor(
            [first, second, second]
        )
        assert not hstrat.does_share_any_common_ancestor(
            [second, first_copy, second]
        )
        assert not hstrat.does_share_any_common_ancestor(
            [first_copy, second, second] * 3
        )
        assert not hstrat.does_share_any_common_ancestor(
            [wrap(second), wrap(first_copy), wrap(second)]
        )
        assert not hstrat.does_share_any_common_ancestor(
            [wrap(first_copy), wrap(second), wrap(second)] * 3
        )

        assert hstrat.does_share_any_common_ancestor([first, first])
        assert hstrat.does_share_any_common_ancestor(
            [wrap(first), wrap(first)]
        )
        assert hstrat.does_share_any_common_ancestor([first_copy, first_copy])
        assert hstrat.does_share_any_common_ancestor([first, first_copy])
        assert hstrat.does_share_any_common_ancestor([first_copy, first])

        assert not hstrat.does_share_any_common_ancestor([second, first])
        assert not hstrat.does_share_any_common_ancestor([first, second])
        assert not hstrat.does_share_any_common_ancestor([second, first_copy])
        assert not hstrat.does_share_any_common_ancestor([first_copy, second])
        assert not hstrat.does_share_any_common_ancestor(
            [wrap(first_copy), wrap(second)]
        )

    assert_validity()
    first.DepositStratum()
    assert_validity()
    second.DepositStratum()
    assert_validity()
    first.DepositStratum()
    assert_validity()

    for __ in range(100):
        first_copy.DepositStratum()
        assert_validity()


@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_does_share_any_common_ancestor_narrow(wrap):
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    assert hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)]) is None
    assert hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)]) is None
    assert hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)]) is None
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2), wrap(c1)])
        is None
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1), wrap(c1)])
        is None
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)] * 3) is None
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)] * 3) is None
    )

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    assert hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)]) is False
    assert hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)]) is False
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2), wrap(c1)])
        is False
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1), wrap(c1)])
        is False
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)] * 3)
        is False
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)] * 3)
        is False
    )

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    c2 = c1.Clone()
    assert hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)]) is None
    assert hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)]) is None
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2), wrap(c1)])
        is None
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1), wrap(c1)])
        is None
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)] * 3) is None
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)] * 3) is None
    )

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    c2 = c1.Clone()
    assert hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)]) is True
    assert hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)]) is True
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2), wrap(c1)])
        is True
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1), wrap(c1)])
        is True
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)] * 3) is True
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)] * 3) is True
    )

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(100):
        c1.DepositStratum()
    c2 = c1.CloneDescendant()
    assert hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)]) is True
    assert hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)]) is True
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2), wrap(c1)])
        is True
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1), wrap(c1)])
        is True
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)] * 3) is True
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)] * 3) is True
    )

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(100):
        c1.DepositStratum()
    c2 = c1.CloneDescendant()
    assert hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)]) is True
    assert hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)]) is True
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2), wrap(c1)])
        is True
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1), wrap(c1)])
        is True
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c1), wrap(c2)] * 3) is True
    )
    assert (
        hstrat.does_share_any_common_ancestor([wrap(c2), wrap(c1)] * 3) is True
    )


@pytest.mark.filterwarnings("ignore:Empty or singleton population.")
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_does_share_any_common_ancestor_singleton(wrap):
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(10):
        assert hstrat.does_share_any_common_ancestor([wrap(c1)]) is None
        c1.DepositStratum()

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(10):
        assert hstrat.does_share_any_common_ancestor([wrap(c1)]) is None
        c2.DepositStratum()


@pytest.mark.filterwarnings("ignore:Empty or singleton population.")
def test_does_share_any_common_ancestor_empty():
    assert hstrat.does_share_any_common_ancestor([]) is None


@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_does_share_any_common_ancestor_generator(wrap):
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(10):
        assert hstrat.does_share_any_common_ancestor(
            [wrap(c1) for __ in range(10)]
        ) == hstrat.does_share_any_common_ancestor(
            (wrap(c1) for __ in range(10))
        )
        c1.DepositStratum()

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(10):
        assert hstrat.does_share_any_common_ancestor(
            [wrap(c2) for __ in range(10)]
        ) == hstrat.does_share_any_common_ancestor(
            (wrap(c2) for __ in range(10))
        )
        c2.DepositStratum()
