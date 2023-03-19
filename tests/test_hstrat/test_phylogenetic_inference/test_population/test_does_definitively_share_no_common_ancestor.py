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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_does_definitively_share_no_common_ancestor1(retention_policy, wrap):
    while True:
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=retention_policy,
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=retention_policy,
        )
        if hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c1), wrap(c2)]
        ):
            assert hstrat.does_definitively_share_no_common_ancestor(
                [wrap(c2), wrap(c1)]
            )
            assert hstrat.does_definitively_share_no_common_ancestor(
                [wrap(c2), wrap(c1)] * 10
            )
            assert not hstrat.does_definitively_share_no_common_ancestor(
                [wrap(c1)] * 10
            )
            for __ in range(100):
                c1.DepositStratum()
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c1), wrap(c2)]
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2), wrap(c1)]
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2), wrap(c1)] * 10
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c1)] * 10 + [wrap(c2)]
                )
            for __ in range(100):
                c2.DepositStratum()
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c1), wrap(c2)]
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2), wrap(c1)]
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2), wrap(c1)] * 10
                )
                assert hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2)] * 10 + [wrap(c1)]
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
        if not hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c1), wrap(c2)]
        ):
            assert not hstrat.does_definitively_share_no_common_ancestor(
                [wrap(c2), wrap(c1)]
            )
            for __ in range(100):
                c1.DepositStratum()
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c1), wrap(c2)]
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2), wrap(c1)]
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2), wrap(c1)] * 10
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2)] * 10 + [wrap(c1)]
                )
            for __ in range(100):
                c2.DepositStratum()
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c1), wrap(c2)]
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2), wrap(c1)]
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c2), wrap(c1)] * 10
                )
                assert not hstrat.does_definitively_share_no_common_ancestor(
                    [wrap(c1)] * 10 + [wrap(c2)]
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
        assert hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c1), wrap(c2)]
        )
        assert hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c2), wrap(c1)]
        )
        assert hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c2), wrap(c1)] * 10
        )
        assert hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c1)] * 10 + [wrap(c2)]
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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_does_definitively_share_no_common_ancestor2(retention_policy, wrap):

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
        stratum_retention_policy=retention_policy,
    )
    c2 = c1.Clone()
    assert not hstrat.does_definitively_share_no_common_ancestor(
        [wrap(c1), wrap(c2)]
    )
    assert not hstrat.does_definitively_share_no_common_ancestor(
        [wrap(c2), wrap(c1)]
    )
    for __ in range(100):
        c1.DepositStratum()
        assert not hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c1), wrap(c2)]
        )
        assert not hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c2), wrap(c1)]
        )
    for __ in range(100):
        c2.DepositStratum()
        assert not hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c1), wrap(c2)]
        )
        assert not hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c2), wrap(c1)]
        )

    for rep in range(100):
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
            stratum_retention_policy=retention_policy,
        )
        c2 = c1.Clone()
        assert not hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c1), wrap(c2)]
        )
        assert not hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c2), wrap(c1)]
        )


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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_does_definitively_share_no_common_ancestor3(retention_policy, wrap):

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
        stratum_retention_policy=retention_policy,
    )
    assert (
        hstrat.does_definitively_share_no_common_ancestor([wrap(c1)]) is None
    )


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

    assert hstrat.does_definitively_share_no_common_ancestor([]) is None


@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_does_definitively_share_no_common_ancestor_generator(wrap):
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(10):
        assert hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c1) for __ in range(10)]
        ) == hstrat.does_definitively_share_no_common_ancestor(
            (wrap(c1) for __ in range(10))
        )
        c1.DepositStratum()

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(10):
        assert hstrat.does_definitively_share_no_common_ancestor(
            [wrap(c2) for __ in range(10)]
        ) == hstrat.does_definitively_share_no_common_ancestor(
            (wrap(c2) for __ in range(10))
        )
        c2.DepositStratum()
