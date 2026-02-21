import os
import re

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


def test_drop_dstream_metadata_default():
    """Default behavior (None) should drop dstream/downstream columns."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_unpack_reconstruct(df)
    dstream_cols = [
        c
        for c in res.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    ]
    # only dstream_data_id and dstream_S should survive by default
    assert set(dstream_cols) == {"dstream_data_id", "dstream_S"}


def test_drop_dstream_metadata_true_raises():
    """Passing drop_dstream_metadata=True should raise NotImplementedError."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    with pytest.raises(NotImplementedError):
        surface_unpack_reconstruct(df, drop_dstream_metadata=True)


def test_drop_dstream_metadata_false():
    """Passing drop_dstream_metadata=False should retain dstream columns."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_unpack_reconstruct(df, drop_dstream_metadata=False)
    assert len(res) > len(df)
    # dstream columns from input should be forwarded
    input_dstream_cols = {
        c
        for c in df.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    }
    output_dstream_cols = {
        c
        for c in res.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    }
    # all original dstream columns should be present in output
    assert input_dstream_cols <= output_dstream_cols
