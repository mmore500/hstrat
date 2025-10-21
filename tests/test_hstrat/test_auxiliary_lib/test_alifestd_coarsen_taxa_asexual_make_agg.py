import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_coarsen_taxa_asexual_make_agg,
    alifestd_make_empty,
)


@pytest.fixture
def sample_phylogeny_df() -> pd.DataFrame:
    # columns to be excluded: id, ancestor_id, ancestor_list
    # override cols: branch_length, destruction_time, edge_length, origin_time
    # other cols: foo, bar
    cols = [
        "id",
        "ancestor_id",
        "ancestor_list",
        "branch_length",
        "destruction_time",
        "edge_length",
        "origin_time",
        "foo",
        "bar",
    ]
    # create an empty DataFrame with just the columns
    return pd.DataFrame({col: [0] for col in cols})


def test_empty_df():
    original_df = alifestd_make_empty(ancestor_id=True)
    result = alifestd_coarsen_taxa_asexual_make_agg(original_df)
    assert isinstance(result, dict)
    assert result == {}


def test_overrides_and_defaults(sample_phylogeny_df):
    agg = alifestd_coarsen_taxa_asexual_make_agg(sample_phylogeny_df)
    # the override columns should map to their override values
    assert agg["destruction_time"] == "last"
    assert agg["origin_time"] == "first"
    # other columns not in overrides should use the default
    assert agg["foo"] == "first"
    assert agg["bar"] == "first"
    # ensure excluded cols are not present
    for excluded in (
        "id",
        "ancestor_id",
        "ancestor_list",
        "branch_length",
        "edge_length",
    ):
        assert excluded not in agg


def test_custom_default(sample_phylogeny_df):
    # if we pass a different default_agg, non-overrides pick that up
    agg = alifestd_coarsen_taxa_asexual_make_agg(
        sample_phylogeny_df,
        default_agg="last",
    )
    # overrides stay the same
    assert "branch_length" not in agg
    assert agg["destruction_time"] == "last"
    assert "edge_length" not in agg
    assert agg["origin_time"] == "first"
    # foo/bar now pick up the new default
    assert agg["foo"] == "last"
    assert agg["bar"] == "last"
