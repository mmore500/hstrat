import pytest

from hstrat import genome_instrumentation, hstrat
from hstrat._auxiliary_lib import flat_len


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
@pytest.mark.parametrize("always_store_rank_in_stratum", [True, False])
@pytest.mark.parametrize(
    "num_deposits",
    [0, 1, 6, 8, 64],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 8, 16, 32, 64],
)
def test_col_to_int(
    impl,
    retention_policy,
    ordered_store,
    always_store_rank_in_stratum,
    num_deposits,
    differentia_bit_width,
    caplog,
):
    column = impl(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_bit_width,
        always_store_rank_in_stratum=always_store_rank_in_stratum,
    )
    for __ in range(num_deposits):
        column.DepositStratum()

    packet = hstrat.col_to_int(column)
    assert packet == hstrat.col_to_int(column)
    assert isinstance(packet, int)
    assert packet.bit_length() <= 8 * (
        (column.GetNumStrataRetained() * differentia_bit_width + 7 + 1) // 8
        + 1  # possible num padding bits header byte
        + 4
    )


def test_col_from_int():
    value = 0x100000008F6
    column = hstrat.col_from_int(
        value,
        differentia_bit_width=1,
        num_strata_deposited_byte_width=4,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    assert not column._always_store_rank_in_stratum
    assert column.GetNumStrataDeposited() == 8
    assert flat_len(column.IterRetainedDifferentia()) == 8
    assert flat_len(column.IterRetainedRanks()) == 8

    assert [*column.IterRankDifferentiaZip()] == [
        (0, 1),
        (1, 1),
        (2, 1),
        (3, 1),
        (4, 0),
        (5, 1),
        (6, 1),
        (7, 0),
    ]


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
@pytest.mark.parametrize("always_store_rank_in_stratum", [True, False])
@pytest.mark.parametrize(
    "num_deposits",
    [0, 1, 6, 8, 64],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 8, 16, 32, 64],
)
def test_col_to_int_then_from_int(
    impl,
    retention_policy,
    ordered_store,
    always_store_rank_in_stratum,
    num_deposits,
    differentia_bit_width,
    caplog,
):
    column = impl(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_bit_width,
        always_store_rank_in_stratum=always_store_rank_in_stratum,
    )
    for __ in range(num_deposits):
        column.DepositStratum()

    assert hstrat.col_to_int(column) == hstrat.col_to_int(column)
    reconstituted = hstrat.col_from_int(
        hstrat.col_to_int(column),
        differentia_bit_width=differentia_bit_width,
        stratum_retention_policy=retention_policy,
    )
    assert reconstituted._ShouldOmitStratumDepositionRank()
    if (
        ordered_store == hstrat.HereditaryStratumOrderedStoreList
        and impl == genome_instrumentation.HereditaryStratigraphicColumn
        and not always_store_rank_in_stratum
    ):
        assert reconstituted == column
    else:
        target_records = hstrat.col_to_records(column)
        # always_store_rank_in_stratum setting is lost
        if "stratum_deposition_ranks" in target_records:
            del target_records["stratum_deposition_ranks"]
        assert hstrat.col_to_records(reconstituted) == target_records