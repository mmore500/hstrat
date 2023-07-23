import json
import logging

import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import log_once_in_a_row


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_policy_to_records(
    retention_policy,
    caplog,
):
    records = hstrat.policy_to_records(retention_policy)
    assert records == hstrat.policy_to_records(retention_policy)
    for entry in [
        "policy_algo",
        "policy",
        "hstrat_version",
    ]:
        assert entry in records
        assert isinstance(records[entry], str)

    assert "policy_spec" in records
    assert isinstance(records["policy_spec"], dict)


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_policy_to_records_then_from_records(
    retention_policy,
    caplog,
):

    assert hstrat.policy_to_records(
        retention_policy
    ) == hstrat.policy_to_records(retention_policy)
    reconstituted = hstrat.policy_from_records(
        hstrat.policy_to_records(retention_policy),
    )
    assert reconstituted == retention_policy


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_policy_to_records_then_from_records_json(
    retention_policy,
    caplog,
):
    records = hstrat.policy_to_records(retention_policy)
    json_str = json.dumps(records)
    reconstituted = hstrat.policy_from_records(json.loads(json_str))
    assert reconstituted == retention_policy


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_policy_to_records_version_warning(
    retention_policy,
    caplog,
):
    # adapted from https://stackoverflow.com/a/48113200
    with caplog.at_level(logging.INFO):
        # clear caplog
        caplog.clear()

        # create a record with a phony version
        record = hstrat.policy_to_records(retention_policy)
        record["hstrat_version"] = "0.0.0"

        # reconstruct phony record
        hstrat.policy_from_records(record)

        # it should have logged a warning
        assert len(caplog.records) >= 1

        # log something to keep the lru cache from supressing the above calls
        log_once_in_a_row("foo")
