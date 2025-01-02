import polars as pl
from tqdm import tqdm

from hstrat._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_try_add_ancestor_list_col,
    alifestd_validate,
)
from hstrat.phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_stub import (
    build_tree_searchtable_cpp_from_exploded,
)


def test_regression_original():
    exploded = pl.DataFrame(
        {
            "dstream_data_id": pl.Series(
                "dstream_data_id",
                [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
                dtype=pl.UInt64,
            ),
            "dstream_T": pl.Series(
                "dstream_T",
                [8, 8, 8, 8, 8, 8, 8, 8, 11, 11, 11, 11, 11, 11, 11, 11],
                dtype=pl.UInt64,
            ),
            "dstream_value_bitwidth": pl.Series(
                "dstream_value_bitwidth",
                [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
                dtype=pl.UInt32,
            ),
            "dstream_value": pl.Series(
                "dstream_value",
                [0, 1, 3, 7, 2, 5, 4, 6, 0, 1, 3, 7, 2, 5, 9, 6],
                dtype=pl.UInt64,
            ),
            "dstream_Tbar": pl.Series(
                "dstream_Tbar",
                [0, 1, 3, 7, 2, 5, 4, 6, 0, 1, 3, 7, 2, 5, 9, 6],
                dtype=pl.UInt64,
            ),
        },
    )
    res = build_tree_searchtable_cpp_from_exploded(
        exploded["dstream_data_id"].to_numpy(),
        exploded["dstream_T"].to_numpy(),
        exploded["dstream_Tbar"].to_numpy(),
        exploded["dstream_value"].to_numpy(),
        tqdm,
    )
    res = pl.DataFrame(res)
    assert alifestd_validate(
        alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert alifestd_is_chronologically_ordered(
        alifestd_try_add_ancestor_list_col(
            res.with_columns(origin_time=pl.col("rank")).to_pandas(),
        ),
    )


def test_regression_distilled():
    exploded = pl.DataFrame(
        {
            "dstream_data_id": pl.Series(
                "dstream_data_id",
                [0, 0, 1],
                dtype=pl.UInt64,
            ),
            "dstream_T": pl.Series(
                "dstream_T",
                [8, 8, 11],
                dtype=pl.UInt64,
            ),
            "dstream_value_bitwidth": pl.Series(
                "dstream_value_bitwidth",
                [
                    8,
                    8,
                    8,
                ],
                dtype=pl.UInt32,
            ),
            "dstream_value": pl.Series(
                "dstream_value",
                [7, 6, 6],
                dtype=pl.UInt64,
            ),
            "dstream_Tbar": pl.Series(
                "dstream_Tbar",
                [7, 6, 6],
                dtype=pl.UInt64,
            ),
        },
    )
    res = build_tree_searchtable_cpp_from_exploded(
        exploded["dstream_data_id"].to_numpy(),
        exploded["dstream_T"].to_numpy(),
        exploded["dstream_Tbar"].to_numpy(),
        exploded["dstream_value"].to_numpy(),
        tqdm,
    )
    res = pl.DataFrame(res)
    assert alifestd_validate(
        alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert alifestd_is_chronologically_ordered(
        alifestd_try_add_ancestor_list_col(
            res.with_columns(origin_time=pl.col("rank")).to_pandas(),
        ),
    )
