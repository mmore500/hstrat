import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
def test_does_definitively_share_no_common_ancestor1(retention_policy):
    while True:
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=retention_policy,
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=retention_policy,
        )
        if hstrat.does_definitively_share_no_common_ancestor([c1, c2]):
            assert hstrat.does_definitively_share_no_common_ancestor([c2, c1])
            assert hstrat.does_definitively_share_no_common_ancestor(
                [c2, c1] * 10
            )
            assert not hstrat.does_definitively_share_no_common_ancestor(
                [c1] * 10
            )
            for __ in range(100):
                c1.DepositStratum()
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [c1, c2]
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [c2, c1]
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [c2, c1] * 10
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [c1] * 10 + [c2]
                )
            for __ in range(100):
                c2.DepositStratum()
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [c1, c2]
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [c2, c1]
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [c2, c1] * 10
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [c2] * 10 + [c1]
                )
            break

    while True:
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=retention_policy,
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=retention_policy,
        )
        if not hstrat.does_definitively_share_no_common_ancestor([c1, c2]):
            assert not hstrat.does_definitively_share_no_common_ancestor(
                [c2, c1]
            )
            for __ in range(100):
                c1.DepositStratum()
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [c1, c2]
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [c2, c1]
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [c2, c1] * 10
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [c2] * 10 + [c1]
                )
            for __ in range(100):
                c2.DepositStratum()
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [c1, c2]
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [c2, c1]
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [c2, c1] * 10
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [c1] * 10 + [c2]
                )
            break

    for rep in range(100):
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
            stratum_retention_policy=retention_policy,
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
            stratum_retention_policy=retention_policy,
        )
        assert hstrat.does_definitively_share_no_common_ancestor([c1, c2])
        assert hstrat.does_definitively_share_no_common_ancestor([c2, c1])
        assert hstrat.does_definitively_share_no_common_ancestor([c2, c1] * 10)
        assert hstrat.does_definitively_share_no_common_ancestor(
            [c1] * 10 + [c2]
        )


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
def test_does_definitively_share_no_common_ancestor2(retention_policy):

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
        stratum_retention_policy=retention_policy,
    )
    c2 = c1.Clone()
    assert not hstrat.does_definitively_share_no_common_ancestor([c1, c2])
    assert not hstrat.does_definitively_share_no_common_ancestor([c2, c1])
    for __ in range(100):
        c1.DepositStratum()
        assert not hstrat.does_definitively_share_no_common_ancestor([c1, c2])
        assert not hstrat.does_definitively_share_no_common_ancestor([c2, c1])
    for __ in range(100):
        c2.DepositStratum()
        assert not hstrat.does_definitively_share_no_common_ancestor([c1, c2])
        assert not hstrat.does_definitively_share_no_common_ancestor([c2, c1])

    for rep in range(100):
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
            stratum_retention_policy=retention_policy,
        )
        c2 = c1.Clone()
        assert not hstrat.does_definitively_share_no_common_ancestor([c1, c2])
        assert not hstrat.does_definitively_share_no_common_ancestor([c2, c1])


@pytest.mark.filterwarnings("ignore:Empty or singleton population.")
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
def test_does_definitively_share_no_common_ancestor3(retention_policy):

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
        stratum_retention_policy=retention_policy,
    )
    c2 = c1.Clone()
    assert hstrat.does_definitively_share_no_common_ancestor([c1]) is None
    assert hstrat.does_definitively_share_no_common_ancestor([c2]) is None
    for __ in range(100):
        c1.DepositStratum()
        assert hstrat.does_definitively_share_no_common_ancestor([c1]) is None
        assert hstrat.does_definitively_share_no_common_ancestor([c2]) is None
    for __ in range(100):
        c2.DepositStratum()
        assert hstrat.does_definitively_share_no_common_ancestor([c1]) is None
        assert hstrat.does_definitively_share_no_common_ancestor([c2]) is None

    for rep in range(100):
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
            stratum_retention_policy=retention_policy,
        )
        c2 = c1.Clone()
        assert hstrat.does_definitively_share_no_common_ancestor([c1]) is None
        assert hstrat.does_definitively_share_no_common_ancestor([c2]) is None


@pytest.mark.filterwarnings("ignore:Empty or singleton population.")
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
def test_does_definitively_share_no_common_ancestor4(retention_policy):

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
        stratum_retention_policy=retention_policy,
    )
    c2 = c1.Clone()
    assert hstrat.does_definitively_share_no_common_ancestor([]) is None
    assert hstrat.does_definitively_share_no_common_ancestor([]) is None
    for __ in range(100):
        c1.DepositStratum()
        assert hstrat.does_definitively_share_no_common_ancestor([]) is None
        assert hstrat.does_definitively_share_no_common_ancestor([]) is None
    for __ in range(100):
        c2.DepositStratum()
        assert hstrat.does_definitively_share_no_common_ancestor([]) is None
        assert hstrat.does_definitively_share_no_common_ancestor([]) is None

    for rep in range(100):
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
            stratum_retention_policy=retention_policy,
        )
        c2 = c1.Clone()
        assert hstrat.does_definitively_share_no_common_ancestor([]) is None
        assert hstrat.does_definitively_share_no_common_ancestor([]) is None


def test_does_definitively_share_no_common_ancestor_generator():
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(10):
        assert hstrat.does_definitively_share_no_common_ancestor(
            [c1 for __ in range(10)]
        ) == hstrat.does_definitively_share_no_common_ancestor(
            (c1 for __ in range(10))
        )
        c1.DepositStratum()

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(10):
        assert hstrat.does_definitively_share_no_common_ancestor(
            [c2 for __ in range(10)]
        ) == hstrat.does_definitively_share_no_common_ancestor(
            (c2 for __ in range(10))
        )
        c2.DepositStratum()
