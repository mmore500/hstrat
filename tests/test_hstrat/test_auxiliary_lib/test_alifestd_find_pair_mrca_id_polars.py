import os
import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import alifestd_to_working_format
from hstrat._auxiliary_lib._alifestd_find_pair_mrca_id_asexual import (
    alifestd_find_pair_mrca_id_asexual,
)
from hstrat._auxiliary_lib._alifestd_find_pair_mrca_id_polars import (
    alifestd_find_pair_mrca_id_polars,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_fuzz_matches_pandas(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    """Verify polars pair mrca matches pandas implementation on real data."""
    df_pl = pl.from_pandas(phylogeny_df)
    ids = phylogeny_df["id"].tolist()
    for i in ids[:5]:
        for j in ids[:5]:
            expected = alifestd_find_pair_mrca_id_asexual(
                phylogeny_df, i, j, mutate=False
            )
            actual = alifestd_find_pair_mrca_id_polars(apply(df_pl), i, j)
            assert actual == expected


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_simple1(apply: typing.Callable):
    """Test a simple 4-node tree: 0 -> 1 -> 2, 0 -> 3."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 1, 0],
            }
        )
    )
    assert alifestd_find_pair_mrca_id_polars(df_pl, 0, 1) == 0
    assert alifestd_find_pair_mrca_id_polars(df_pl, 1, 2) == 1
    assert alifestd_find_pair_mrca_id_polars(df_pl, 2, 3) == 0
    assert alifestd_find_pair_mrca_id_polars(df_pl, 2, 2) == 2
    assert alifestd_find_pair_mrca_id_polars(df_pl, 0, 0) == 0


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_single_node(apply: typing.Callable):
    """A single root node: MRCA with self is self."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
            }
        )
    )
    assert alifestd_find_pair_mrca_id_polars(df_pl, 0, 0) == 0


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_multiple_roots_disjoint(apply: typing.Callable):
    """Two disjoint roots should return None."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        )
    )
    assert alifestd_find_pair_mrca_id_polars(df_pl, 0, 1) is None
    assert alifestd_find_pair_mrca_id_polars(df_pl, 1, 2) is None
    assert alifestd_find_pair_mrca_id_polars(df_pl, 0, 0) == 0


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_multiple_roots_partial(apply: typing.Callable):
    """Forest: tree1 = {0, 1}, tree2 = {2, 3}."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 2, 2],
            }
        )
    )
    assert alifestd_find_pair_mrca_id_polars(df_pl, 0, 1) == 0
    assert alifestd_find_pair_mrca_id_polars(df_pl, 2, 3) == 2
    assert alifestd_find_pair_mrca_id_polars(df_pl, 0, 2) is None
    assert alifestd_find_pair_mrca_id_polars(df_pl, 1, 3) is None


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_chain(apply: typing.Callable):
    """Straight chain: 0 -> 1 -> 2 -> 3."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 1, 2],
            }
        )
    )
    assert alifestd_find_pair_mrca_id_polars(df_pl, 0, 3) == 0
    assert alifestd_find_pair_mrca_id_polars(df_pl, 1, 3) == 1
    assert alifestd_find_pair_mrca_id_polars(df_pl, 2, 3) == 2


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_with_ancestor_list_col(apply: typing.Callable):
    """Test that ancestor_list is correctly converted to ancestor_id."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_list": ["[None]", "[0]", "[0]", "[1]"],
            }
        )
    )
    # Tree: 0->1->3, 0->2
    assert alifestd_find_pair_mrca_id_polars(df_pl, 2, 3) == 0
    assert alifestd_find_pair_mrca_id_polars(df_pl, 1, 3) == 1
    assert alifestd_find_pair_mrca_id_polars(df_pl, 1, 2) == 0


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_does_not_mutate_input(apply: typing.Callable):
    """Verify the input dataframe is not mutated."""
    df_pl = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 0],
        }
    )
    original_data = df_pl.clone()

    alifestd_find_pair_mrca_id_polars(apply(df_pl), 1, 2)

    assert df_pl.columns == original_data.columns
    assert df_pl.equals(original_data)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_bypass_kwargs(apply: typing.Callable):
    """Test that is_topologically_sorted and has_contiguous_ids kwargs work."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 1, 0],
            }
        )
    )
    result = alifestd_find_pair_mrca_id_polars(
        df_pl,
        2,
        3,
        is_topologically_sorted=True,
        has_contiguous_ids=True,
    )
    assert result == 0
