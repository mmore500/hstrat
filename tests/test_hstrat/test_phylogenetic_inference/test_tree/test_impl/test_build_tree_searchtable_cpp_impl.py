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
    copy_records_to_dict,
    placeholder_value,
)


def test_collapse_unifurcations_singleton():
    records = Records(1)
    records = collapse_unifurcations(records, dropped_only=False)
    assert len(records) == 1


def test_collapse_all_unifurcations_linear_tree():
    # 0 <- 1 <- 2 <- 3 <- 4 <- 5 <- 6 <- 7
    records = Records(8)
    records.addRecord(1, 1, 0, 0, 2, 1, 1, 1, 1)
    records.addRecord(2, 2, 1, 1, 3, 2, 2, 2, 2)
    records.addRecord(3, 3, 2, 2, 4, 3, 3, 3, 3)
    records.addRecord(4, 4, 3, 3, 5, 4, 4, 4, 4)
    records.addRecord(5, 5, 4, 4, 6, 5, 5, 5, 5)
    records.addRecord(6, 6, 5, 5, 7, 6, 6, 6, 6)
    records.addRecord(7, 7, 6, 6, 7, 7, 7, 7, 7)

    records = collapse_unifurcations(records, dropped_only=False)
    assert len(records) == 2

    result = copy_records_to_dict(records)

    # 0 <- 7(1)
    expected = {
        "dstream_data_id": [placeholder_value, 7],
        "id": [0, 1],
        "ancestor_id": [0, 0],
        "search_ancestor_id": [placeholder_value] * 2,
        "search_first_child_id": [placeholder_value] * 2,
        "search_prev_sibling_id": [placeholder_value] * 2,
        "search_next_sibling_id": [placeholder_value] * 2,
        "rank": [0, 7],
        "differentia": [0, 7],
    }

    for key in expected:
        expected_value = expected[key]
        assert result[key] == expected_value, key


def test_collapse_all_unifurcations_branched_tree():
    # 0 <- 1 <- 3
    #  \ <- 2 <- 4 <- 5 <- 6
    #                  \ <- 7
    records = Records(8)
    records.addRecord(1, 1, 0, 0, 3, 1, 2, 1, 1)
    records.addRecord(2, 2, 0, 0, 4, 1, 2, 1, 2)
    records.addRecord(3, 3, 1, 1, 3, 3, 3, 2, 1)
    records.addRecord(4, 4, 2, 2, 5, 4, 4, 2, 1)
    records.addRecord(5, 5, 4, 4, 5, 5, 5, 3, 0)
    records.addRecord(6, 6, 5, 5, 6, 6, 7, 4, 1)
    records.addRecord(7, 7, 5, 5, 7, 6, 7, 4, 2)
    records = collapse_unifurcations(records, dropped_only=False)
    assert len(records) == 5

    result = copy_records_to_dict(records)

    # 0 <- 3(1)
    #  \ <- 5(2) <- 6(3)
    #         \  <- 7(4)
    expected = {
        "dstream_data_id": [placeholder_value, 3, 5, 6, 7],
        "id": [0, 1, 2, 3, 4],
        "ancestor_id": [0, 0, 0, 2, 2],
        "search_ancestor_id": [placeholder_value] * 5,
        "search_first_child_id": [placeholder_value] * 5,
        "search_prev_sibling_id": [placeholder_value] * 5,
        "search_next_sibling_id": [placeholder_value] * 5,
        "rank": [0, 2, 3, 4, 4],
        "differentia": [0, 1, 0, 1, 2],
    }

    for key, value in result.items():
        expected_value = expected[key]
        assert value == expected_value, key


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
