import logging

import pytest

from hstrat import genome_instrumentation, hstrat
from hstrat._auxiliary_lib import get_hstrat_version, log_once_in_a_row


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
    caplog,
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

    # adapted from https://stackoverflow.com/a/48113200
    with caplog.at_level(logging.INFO):
        # clear caplog
        caplog.clear()

        # create a record with a phony version
        record = hstrat.col_to_records(column)
        record["hstrat_version"] = "0.0.0"

        # reconstruct phony record
        hstrat.col_from_records(record)

        # it should have logged one warning
        assert len(caplog.records) == 1
        # retrieve it
        logged = next(iter(caplog.records))

        assert logged.levelno == logging.INFO
        assert logged.name == "hstrat"
        assert logged.module == "_log_once_in_a_row"
        assert (
            logged.message
            == f"""col_from_records version mismatch, record is version {
                record["hstrat_version"]
            } and software is version {
                get_hstrat_version()
            }"""
        )

        # log something to keep the lru cache from supressing the above calls
        log_once_in_a_row("foo")