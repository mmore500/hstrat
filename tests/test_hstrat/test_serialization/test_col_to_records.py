import json
import logging

import pytest

from hstrat import genome_instrumentation, hstrat
from hstrat._auxiliary_lib import log_once_in_a_row


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
def test_col_to_records(
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
        always_store_rank_in_stratum=always_store_rank_in_stratum,
    )
    for __ in range(num_deposits):
        column.DepositStratum()

    records = hstrat.col_to_records(column)
    assert records == hstrat.col_to_records(column)
    for entry in [
        "policy_algo",
        "policy",
        "num_strata_deposited",
        "differentiae",
        "differentia_bit_width",
        "hstrat_version",
    ]:
        assert entry in records
        assert isinstance(records[entry], (int, str))

    assert "policy_spec" in records
    assert isinstance(records["policy_spec"], dict)


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
def test_col_to_records_then_from_records(
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

    assert hstrat.col_to_records(column) == hstrat.col_to_records(column)
    records = hstrat.col_to_records(column)
    reconstituted = hstrat.col_from_records(
        records, differentiae_byte_bit_order="big"
    )
    if column.GetNumStrataRetained() >= 20:
        assert reconstituted != hstrat.col_from_records(
            records, differentiae_byte_bit_order="little"
        )
    if (
        ordered_store == hstrat.HereditaryStratumOrderedStoreList
        and impl == genome_instrumentation.HereditaryStratigraphicColumn
    ):
        assert reconstituted == column
    else:
        assert hstrat.col_to_records(reconstituted) == hstrat.col_to_records(
            column
        )


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
def test_col_to_records_then_from_records_with_annotations(
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
        initial_stratum_annotation=9,
        always_store_rank_in_stratum=always_store_rank_in_stratum,
    )
    for gen in range(num_deposits):
        column.DepositStratum(annotation=gen)

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
def test_col_to_records_then_from_records_json(
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

    records = hstrat.col_to_records(column)
    json_str = json.dumps(records)
    reconstituted = hstrat.col_from_records(json.loads(json_str))
    if (
        ordered_store == hstrat.HereditaryStratumOrderedStoreList
        and impl == genome_instrumentation.HereditaryStratigraphicColumn
    ):
        assert reconstituted == column
    else:
        assert hstrat.col_to_records(reconstituted) == hstrat.col_to_records(
            column
        )


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
def test_col_to_records_version_warning(
    impl,
    retention_policy,
    ordered_store,
    num_deposits,
    differentia_bit_width,
    caplog,
):
    column = impl(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_bit_width,
    )
    for __ in range(num_deposits):
        column.DepositStratum()

    # adapted from https://stackoverflow.com/a/48113200
    with caplog.at_level(logging.INFO):
        # clear caplog
        caplog.clear()

        # create a record with a phony version
        record = hstrat.col_to_records(column)
        record["hstrat_version"] = "0.0.0"

        # reconstruct phony record
        hstrat.col_from_records(record)

        # it should have logged a warning
        assert len(caplog.records)

        # log something to keep the lru cache from supressing the above calls
        log_once_in_a_row("foo")
