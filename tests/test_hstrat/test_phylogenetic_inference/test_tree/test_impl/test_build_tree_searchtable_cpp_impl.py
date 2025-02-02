import polars as pl
from tqdm import tqdm

from hstrat._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_try_add_ancestor_list_col,
    alifestd_validate,
)
from hstrat.phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_stub import (
    Records,
    build_tree_searchtable_cpp_from_exploded,
    collapse_unifurcations,
    placeholder_value,
)


def test_collapse_unifurcations_singleton():
    records = Records(1)
    records = collapse_unifurcations(records, dropped_only=False)
    assert len(records) == 1


def test_collapse_all_unifurcations_linear_tree():
    records = Records(8)
    records.addRecord(placeholder_value, 1, 0, 0, 2, 1, 1, 1, 1)
    records.addRecord(placeholder_value, 2, 1, 1, 3, 2, 2, 2, 2)
    records.addRecord(placeholder_value, 3, 2, 2, 4, 3, 3, 3, 3)
    records.addRecord(placeholder_value, 4, 3, 3, 5, 4, 4, 4, 4)
    records.addRecord(placeholder_value, 5, 4, 4, 6, 5, 5, 5, 5)
    records.addRecord(placeholder_value, 6, 5, 5, 7, 6, 6, 6, 6)
    records.addRecord(placeholder_value, 7, 6, 6, 8, 7, 7, 7, 7)
    records = collapse_unifurcations(records, dropped_only=False)
    assert len(records) == 2


def test_collapse_all_unifurcations_branched_tree():
    records = Records(8)
    records.addRecord(placeholder_value, 1, 0, 0, 3, 1, 2, 1, 1)
    records.addRecord(placeholder_value, 2, 0, 0, 4, 1, 2, 1, 2)
    records.addRecord(placeholder_value, 3, 1, 1, 3, 3, 3, 2, 1)
    records.addRecord(placeholder_value, 4, 2, 2, 5, 4, 4, 2, 1)
    records.addRecord(placeholder_value, 5, 4, 4, 5, 5, 5, 3, 0)
    records.addRecord(placeholder_value, 6, 5, 5, 6, 6, 7, 4, 1)
    records.addRecord(placeholder_value, 7, 5, 5, 7, 6, 7, 4, 2)
    records = collapse_unifurcations(records, dropped_only=False)
    assert len(records) == 5


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
    ).select(
        pl.col(
            "dstream_data_id",
            "dstream_T",
            "dstream_Tbar",
            "dstream_value",
        )
        .sort_by("dstream_Tbar")
        .over(partition_by="dstream_data_id"),
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
    ).select(
        pl.col(
            "dstream_data_id",
            "dstream_T",
            "dstream_Tbar",
            "dstream_value",
        )
        .sort_by("dstream_Tbar")
        .over(partition_by="dstream_data_id"),
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
