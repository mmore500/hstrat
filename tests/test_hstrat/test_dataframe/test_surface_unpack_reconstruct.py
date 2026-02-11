import os

import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_try_add_ancestor_list_col,
    alifestd_validate,
)
from hstrat.dataframe import surface_unpack_reconstruct

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize("pa_source_type", ["memory_map", "OSFile"])
def test_smoke(pa_source_type: str):
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_unpack_reconstruct(df, pa_source_type=pa_source_type)
    assert len(res) > len(df)
    assert alifestd_validate(
        alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert alifestd_is_chronologically_ordered(
        alifestd_try_add_ancestor_list_col(
            res.with_columns(origin_time=pl.col("hstrat_rank")).to_pandas(),
        ),
    )
