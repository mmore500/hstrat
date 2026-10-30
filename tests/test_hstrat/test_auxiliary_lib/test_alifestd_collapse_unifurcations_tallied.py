import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_collapse_unifurcations_tallied_asexual,
    alifestd_collapse_unifurcations_tallied_polars,
)


def _make_df() -> pd.DataFrame:
    # 0 (root) <- 1 (unifurcation) <- 2 <- 3, 4 (leaves)
    return pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 2],
            "tally": pd.array([0, 2, 1, 0, 0], dtype="uint32"),
        },
    )


def _check(res: pd.DataFrame) -> None:
    assert 1 not in res["id"].tolist()
    tallies = dict(zip(res["id"], res["tally"]))
    # node 2 tallies itself plus node 1 and node 1's prior tally
    assert tallies[2] == 1 + 1 + 2
    assert tallies[3] == 0 and tallies[4] == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_asexual(mutate: bool):
    df = _make_df()
    original = df.copy()
    res = alifestd_collapse_unifurcations_tallied_asexual(
        df, "tally", mutate=mutate
    )
    _check(res)
    if not mutate:
        pd.testing.assert_frame_equal(df, original)


def test_polars():
    res = alifestd_collapse_unifurcations_tallied_polars(
        pl.from_pandas(_make_df()), "tally"
    )
    assert res["tally"].dtype == pl.UInt32
    _check(res.to_pandas())


def test_null_tally_raises():
    df = pl.from_pandas(_make_df()).with_columns(
        pl.when(pl.col("id") == 2)
        .then(None)
        .otherwise(pl.col("tally"))
        .alias("tally"),
    )
    with pytest.raises(AssertionError):
        alifestd_collapse_unifurcations_tallied_polars(df, "tally")
    with pytest.raises(AssertionError):
        alifestd_collapse_unifurcations_tallied_asexual(
            df.to_pandas(), "tally"
        )
