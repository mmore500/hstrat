import copy
from typing import Dict

import pytest

from hstrat.serialization._impl import col_records_from_pop_records


@pytest.fixture()
def pop_records() -> Dict:
    return {
        "columns": [
            {"id": 1, "name": "column_1"},
            {"id": 2, "name": "column_2"},
            {"id": 3, "name": "column_3"},
        ],
        "policy": "some_policy",
        "policy_algo": "some_algo",
        "policy_spec": "some_spec",
        "differentia_bit_width": 16,
        "hstrat_version": 1.0,
    }


def test_col_records_from_pop_records(pop_records: Dict):
    col_records = list(col_records_from_pop_records(pop_records))
    assert len(col_records) == 3

    for col_record in col_records:
        assert isinstance(col_record, dict)
        assert "id" in col_record
        assert "name" in col_record
        assert col_record["policy"] == "some_policy"
        assert col_record["policy_algo"] == "some_algo"
        assert col_record["policy_spec"] == "some_spec"
        assert col_record["differentia_bit_width"] == 16
        assert col_record["hstrat_version"] == 1.0


def test_col_records_from_pop_records_mutate(pop_records: Dict):
    col_records = list(col_records_from_pop_records(pop_records, mutate=True))
    assert len(col_records) == 3

    for col_record in col_records:
        assert isinstance(col_record, dict)
        assert "id" in col_record
        assert "name" in col_record
        assert col_record["policy"] == "some_policy"
        assert col_record["policy_algo"] == "some_algo"
        assert col_record["policy_spec"] == "some_spec"
        assert col_record["differentia_bit_width"] == 16
        assert col_record["hstrat_version"] == 1.0

    assert pop_records["columns"] == col_records


def test_col_records_from_pop_records_empty():
    pop_records = {"columns": []}
    col_records = list(col_records_from_pop_records(pop_records))
    assert len(col_records) == 0


def test_col_records_from_pop_records_no_mutate(pop_records: Dict):
    pop_records_copy = copy.deepcopy(pop_records)
    col_records = list(
        col_records_from_pop_records(pop_records_copy, mutate=False)
    )
    assert len(col_records) == 3

    for col_record in col_records:
        assert isinstance(col_record, dict)
        assert "id" in col_record
        assert "name" in col_record
        assert col_record["policy"] == "some_policy"
        assert col_record["policy_algo"] == "some_algo"
        assert col_record["policy_spec"] == "some_spec"
        assert col_record["differentia_bit_width"] == 16
        assert col_record["hstrat_version"] == 1.0

    assert pop_records == pop_records_copy
