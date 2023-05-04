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
def test_col_to_dataframe(
    retention_policy,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
    )

    for generation in range(100):
        column.DepositStratum()

    df = hstrat.col_to_dataframe(column)
    assert len(df) == column.GetNumStrataRetained()
    assert df["rank"].max() == column.GetNumStrataDeposited() - 1
