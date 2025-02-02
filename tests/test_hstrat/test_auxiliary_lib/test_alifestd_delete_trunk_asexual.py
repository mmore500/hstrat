import os

import pandas as pd
import pandas.testing as pdt
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_collapse_unifurcations,
    alifestd_delete_trunk_asexual,
    alifestd_delete_trunk_asexual_polars,
    alifestd_prefix_roots,
    alifestd_test_leaves_isomorphic_asexual,
    alifestd_to_working_format,
    alifestd_validate,
)

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_delete_trunk_asexual_no_trunk_column(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
        }
    )
    with pytest.raises(ValueError):
        alifestd_delete_trunk_asexual(df, mutate=mutate)
    with pytest.raises(ValueError):
        alifestd_delete_trunk_asexual_polars(pl.from_pandas(df))


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_delete_trunk_asexual_single_trunk(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[]"],
            "is_trunk": [True],
        }
    )
    original_df = df.copy()
    result = alifestd_delete_trunk_asexual(df, mutate=mutate)
    assert alifestd_validate(result)
    assert len(result) == 0

    if not mutate:
        assert original_df.equals(df)

    df.drop(columns=["ancestor_list"], inplace=True)
    result.drop(columns=["ancestor_list"], inplace=True)
    df["ancestor_id"] = [0]
    pdt.assert_frame_equal(
        result,
        alifestd_delete_trunk_asexual_polars(pl.from_pandas(df)).to_pandas(),
        check_dtype=False,
    )


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_delete_trunk_asexual_no_collapse_needed1(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 8],
            "ancestor_id": [0, 0],
            "ancestor_list": ["[none]", "[0]"],
            "is_trunk": [True, False],
        }
    )
    original_df = df.copy()
    result = alifestd_delete_trunk_asexual(df)
    assert alifestd_validate(result)

    expected = pd.DataFrame(
        {
            "id": [8],
            "ancestor_list": ["[none]"],
            "is_trunk": [False],
        }
    )
    pd.testing.assert_frame_equal(
        result[expected.columns].reset_index(drop=True), expected
    )

    if not mutate:
        assert original_df.equals(df)

    df.drop(columns=["ancestor_list"], inplace=True)
    result.drop(columns=["ancestor_list"], inplace=True)
    with pytest.raises(NotImplementedError):
        alifestd_delete_trunk_asexual_polars(pl.from_pandas(df)).to_pandas(),


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_delete_trunk_asexual_no_collapse_needed2(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "is_trunk": [True, True],
        }
    )
    original_df = df.copy()
    result = alifestd_delete_trunk_asexual(df)
    assert alifestd_validate(result)
    assert len(result) == 0

    if not mutate:
        assert original_df.equals(df)

    df.drop(columns=["ancestor_list"], inplace=True)
    result.drop(columns=["ancestor_list"], inplace=True)
    df["ancestor_id"] = [0, 0]
    pdt.assert_frame_equal(
        result,
        alifestd_delete_trunk_asexual_polars(pl.from_pandas(df)).to_pandas(),
        check_dtype=False,
    )


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_delete_trunk_asexual_no_collapse_needed3(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "ancestor_list": ["[none]", "[0]", "[1]"],
            "is_trunk": [False, False, False],
        }
    )
    original_df = df.copy()
    result = alifestd_delete_trunk_asexual(df)
    assert alifestd_validate(result)
    pd.testing.assert_frame_equal(result[df.columns], df)

    if not mutate:
        assert df.equals(original_df)

    df.drop(columns=["ancestor_list"], inplace=True)
    result.drop(columns=["ancestor_list"], inplace=True)
    pdt.assert_frame_equal(
        result,
        alifestd_delete_trunk_asexual_polars(pl.from_pandas(df)).to_pandas(),
        check_dtype=False,
    )


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_delete_trunk_asexual_collapse1(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 4, 3, 5],
            "ancestor_id": [0, 0, 1, 2, 0, 5],
            "ancestor_list": ["[none]", "[0]", "[1]", "[2]", "[0]", "[none]"],
            "is_trunk": [True, True, True, False, False, False],
        }
    )
    original_df = df.copy()
    result = alifestd_delete_trunk_asexual(df)
    assert alifestd_validate(result)

    expected = pd.DataFrame(
        {
            "id": [4, 3, 5],
            "ancestor_id": [4, 3, 5],
            "ancestor_list": ["[none]", "[none]", "[none]"],
            "is_trunk": [False, False, False],
        }
    )
    pd.testing.assert_frame_equal(result[expected.columns], expected)

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_delete_trunk_asexual_collapse2(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[1]",
                "[0]",
                "[0]",
                "[2]",
                "[3]",
            ],
            "is_trunk": [True, True, True, False, True, True, False],
        }
    )
    original_df = df.copy()
    result = alifestd_delete_trunk_asexual(df)
    assert alifestd_validate(result)

    expected = pd.DataFrame(
        {
            "id": [3, 6],
            "ancestor_list": ["[none]", "[3]"],
            "is_trunk": [False, False],
        }
    )
    pd.testing.assert_frame_equal(result[expected.columns], expected)

    if not mutate:
        assert df.equals(original_df)

    df.drop(columns=["ancestor_list"], inplace=True)
    result.drop(columns=["ancestor_list"], inplace=True)
    df["ancestor_id"] = [0, 0, 1, 0, 0, 2, 3]
    pdt.assert_frame_equal(
        result,
        alifestd_delete_trunk_asexual_polars(pl.from_pandas(df)).to_pandas(),
        check_dtype=False,
    )


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_delete_trunk_asexual_noncontiguous_trunk(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "is_trunk": [True, False, True],
        }
    )
    original_df = df.copy()
    with pytest.raises(ValueError):
        alifestd_delete_trunk_asexual(df)

    if not mutate:
        assert df.equals(original_df)

    df.drop(columns=["ancestor_list"], inplace=True)
    df["ancestor_id"] = [0, 0, 1]
    with pytest.raises(ValueError):
        alifestd_delete_trunk_asexual_polars(pl.from_pandas(df))


def test_alifestd_delete_trunk_asexual_unifurcation():
    phylo = pd.read_csv(f"{assets}/trunktestphylo.csv")
    phylo["is_trunk"] = phylo["hstrat_rank"] < 64
    assert alifestd_test_leaves_isomorphic_asexual(
        phylo, phylo, taxon_label="dstream_data_id"
    )
    assert alifestd_test_leaves_isomorphic_asexual(
        phylo,
        alifestd_collapse_unifurcations(phylo),
        taxon_label="dstream_data_id",
    )
    assert alifestd_test_leaves_isomorphic_asexual(
        phylo,
        alifestd_collapse_unifurcations(phylo),
        taxon_label="dstream_data_id",
    )
    assert alifestd_test_leaves_isomorphic_asexual(
        alifestd_delete_trunk_asexual(phylo),
        alifestd_delete_trunk_asexual(phylo),
        taxon_label="dstream_data_id",
    )
    assert alifestd_test_leaves_isomorphic_asexual(
        alifestd_collapse_unifurcations(alifestd_delete_trunk_asexual(phylo)),
        alifestd_delete_trunk_asexual(phylo),
        taxon_label="dstream_data_id",
    )

    pdt.assert_frame_equal(
        alifestd_delete_trunk_asexual(phylo),
        alifestd_delete_trunk_asexual_polars(
            pl.from_pandas(phylo)
        ).to_pandas(),
        check_dtype=False,
    )

    def clean(df: pd.DataFrame, allow_id_reassign: bool) -> pd.DataFrame:
        return alifestd_to_working_format(
            alifestd_collapse_unifurcations(
                alifestd_prefix_roots(
                    df,
                    allow_id_reassign=allow_id_reassign,
                    origin_time=64,
                ),
            ),
        )

    phylo["origin_time"] = phylo["hstrat_rank"]
    for allow_id_reassign in [True, False]:
        assert alifestd_test_leaves_isomorphic_asexual(
            clean(
                alifestd_delete_trunk_asexual(phylo),
                allow_id_reassign=allow_id_reassign,
            ),
            clean(
                alifestd_delete_trunk_asexual(
                    alifestd_collapse_unifurcations(phylo),
                ),
                allow_id_reassign=allow_id_reassign,
            ),
            taxon_label="dstream_data_id",
        )

        assert alifestd_test_leaves_isomorphic_asexual(
            clean(
                alifestd_delete_trunk_asexual(phylo),
                allow_id_reassign=allow_id_reassign,
            ),
            clean(
                alifestd_delete_trunk_asexual(
                    alifestd_collapse_unifurcations(phylo),
                ),
                allow_id_reassign=True,
            ),
            taxon_label="dstream_data_id",
        )

        assert alifestd_test_leaves_isomorphic_asexual(
            clean(
                alifestd_delete_trunk_asexual(phylo),
                allow_id_reassign=False,
            ),
            clean(
                alifestd_delete_trunk_asexual(
                    alifestd_collapse_unifurcations(phylo),
                ),
                allow_id_reassign=allow_id_reassign,
            ),
            taxon_label="dstream_data_id",
        )
