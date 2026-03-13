import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(3),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.perfect_resolution_algo.Policy(),
    ],
)
@pytest.mark.parametrize("bit_width", [1, 8, 64])
def test_assemblage_to_ascii_smoke(policy, bit_width):
    cols = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
            stratum_differentia_bit_width=bit_width,
        )
        for _ in range(3)
    ]
    for col in cols:
        for _ in range(20):
            col.DepositStratum()

    assemblage = hstrat.pop_to_assemblage(cols)
    result = hstrat.assemblage_to_ascii(assemblage)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize(
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(3),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.perfect_resolution_algo.Policy(),
    ],
)
def test_assemblage_to_ascii_key(policy):
    cols = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
            stratum_differentia_bit_width=8,
        )
        for _ in range(2)
    ]
    for col in cols:
        for _ in range(10):
            col.DepositStratum()

    assemblage = hstrat.pop_to_assemblage(cols)

    result_with_key = hstrat.assemblage_to_ascii(assemblage, key=True)
    result_without_key = hstrat.assemblage_to_ascii(assemblage, key=False)

    assert "*: retained stratum" in result_with_key
    assert "*: retained stratum" not in result_without_key


@pytest.mark.parametrize(
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(3),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.perfect_resolution_algo.Policy(),
    ],
)
def test_assemblage_to_ascii_time_bookends(policy):
    cols = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
            stratum_differentia_bit_width=8,
        )
        for _ in range(2)
    ]
    for col in cols:
        for _ in range(10):
            col.DepositStratum()

    assemblage = hstrat.pop_to_assemblage(cols)

    result_with_bookends = hstrat.assemblage_to_ascii(
        assemblage, time_bookends=True
    )
    result_without_bookends = hstrat.assemblage_to_ascii(
        assemblage, time_bookends=False
    )

    assert "MOST ANCIENT" in result_with_bookends
    assert "MOST RECENT" in result_with_bookends
    assert "MOST ANCIENT" not in result_without_bookends
    assert "MOST RECENT" not in result_without_bookends


def test_assemblage_to_ascii_single_specimen():
    policy = hstrat.fixed_resolution_algo.Policy(3)
    col = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=8,
    )
    for _ in range(10):
        col.DepositStratum()

    assemblage = hstrat.pop_to_assemblage([col])
    result = hstrat.assemblage_to_ascii(assemblage)

    assert isinstance(result, str)
    assert "specimen 0" in result
    assert "specimen 1" not in result


def test_assemblage_to_ascii_different_num_strata():
    """Test with columns that have different numbers of deposited strata."""
    policy = hstrat.fixed_resolution_algo.Policy(3)
    cols = []
    for i in range(3):
        col = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
            stratum_differentia_bit_width=8,
        )
        for _ in range(10 + i * 5):
            col.DepositStratum()
        cols.append(col)

    assemblage = hstrat.pop_to_assemblage(cols)
    result = hstrat.assemblage_to_ascii(assemblage)

    assert isinstance(result, str)
    assert "░" in result  # Should have missing strata markers


def test_assemblage_to_ascii_has_rank_column():
    policy = hstrat.fixed_resolution_algo.Policy(3)
    cols = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
            stratum_differentia_bit_width=8,
        )
        for _ in range(2)
    ]
    for col in cols:
        for _ in range(10):
            col.DepositStratum()

    assemblage = hstrat.pop_to_assemblage(cols)
    result = hstrat.assemblage_to_ascii(assemblage)

    assert "rank" in result


def test_assemblage_to_ascii_differentia_format():
    """Test that differentia values are formatted as hex with asterisk."""
    policy = hstrat.perfect_resolution_algo.Policy()
    col = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=8,
    )
    for _ in range(5):
        col.DepositStratum()

    assemblage = hstrat.pop_to_assemblage([col])
    result = hstrat.assemblage_to_ascii(assemblage)

    # Each retained stratum should have hex value followed by *
    lines = result.split("\n")
    data_lines = [
        line
        for line in lines
        if "|" in line and "*" in line and "rank" not in line
    ]
    assert len(data_lines) > 0
    for line in data_lines:
        assert "*" in line
