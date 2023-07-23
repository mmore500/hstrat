import json
import logging
import operator

import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import get_hstrat_version, log_once_in_a_row


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=4
        ),
    ],
)
@pytest.mark.parametrize(
    "num_deposits",
    [0, 1, 6, 8, 64, 65],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 20, 32, 64, 129],
)
def test_specimen_from_records1(
    retention_policy,
    num_deposits,
    differentia_bit_width,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_bit_width,
    ).CloneNthDescendant(num_deposits)

    specimen = hstrat.specimen_from_records(hstrat.col_to_records(column))
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(column.IterRetainedRanks(), specimen.GetRankIndex()),
        )
    )
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(
                column.IterRetainedDifferentia(), specimen.GetDifferentiaVals()
            ),
        )
    )


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=4
        ),
    ],
)
@pytest.mark.parametrize(
    "num_deposits",
    [0, 1, 6, 8, 64, 65],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 20, 32, 64],
)
def test_col_to_records_then_to_specimen_json(
    retention_policy,
    num_deposits,
    differentia_bit_width,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_bit_width,
    ).CloneNthDescendant(num_deposits)

    records = hstrat.col_to_records(column)
    json_str = json.dumps(records)
    reconstituted_records = json.loads(json_str)
    specimen = hstrat.specimen_from_records(reconstituted_records)
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(column.IterRetainedRanks(), specimen.GetRankIndex()),
        )
    )
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(
                column.IterRetainedDifferentia(), specimen.GetDifferentiaVals()
            ),
        )
    )


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=4
        ),
    ],
)
@pytest.mark.parametrize(
    "num_deposits",
    [0, 1, 6, 8, 64, 65],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 20, 32, 64],
)
def test_specimen_from_records2(
    retention_policy,
    num_deposits,
    differentia_bit_width,
    caplog,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_bit_width,
    ).CloneNthDescendant(num_deposits)

    # adapted from https://stackoverflow.com/a/48113200
    with caplog.at_level(logging.INFO):
        # clear caplog
        caplog.clear()

        # create a record with a phony version
        record = hstrat.col_to_records(column)
        record["hstrat_version"] = "0.0.0"

        # reconstruct phony record
        hstrat.specimen_from_records(record)

        # it should have logged one warning
        assert len(caplog.records) == 1
        # retrieve it
        logged = next(iter(caplog.records))

        assert logged.levelno == logging.INFO
        assert logged.name == "hstrat"
        assert logged.module == "_log_once_in_a_row"
        assert (
            logged.message
            == f"""specimen_from_records version mismatch, record is version {
                record["hstrat_version"]
            } and software is version {
                get_hstrat_version()
            }"""
        )

        # log something to keep the lru cache from supressing the above calls
        log_once_in_a_row("foo")
