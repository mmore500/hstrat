import pytest

from hstrat import genome_instrumentation, hstrat


@pytest.mark.parametrize(
    "impl",
    [genome_instrumentation.HereditaryStratigraphicColumn],
    # TODO
    # genome_instrumentation._HereditaryStratigraphicColumn_.impls,
)
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
        None,
    ],
)
@pytest.mark.parametrize(
    "num_deposits",
    [0, 1, 6, 8, 64],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 8, 16, 32, 64],
)
def test_col_to_records(
    impl,
    retention_policy,
    ordered_store,
    num_deposits,
    differentia_bit_width,
):
    column = impl(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    for __ in range(num_deposits):
        column.DepositStratum()

    assert hstrat.col_to_records(column) == hstrat.col_to_records(column)
    reconstituted = hstrat.col_from_records(hstrat.col_to_records(column))
    if (
        ordered_store == hstrat.HereditaryStratumOrderedStoreList
        and impl == genome_instrumentation.HereditaryStratigraphicColumn
    ):
        assert reconstituted == column
    else:
        assert hstrat.col_to_records(reconstituted) == hstrat.col_to_records(
            column
        )
