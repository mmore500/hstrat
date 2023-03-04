from iterpop import iterpop as ip
import pandas as pd

from hstrat._auxiliary_lib import alifestd_find_root_ids
import hstrat.phylogenetic_inference.tree._impl as impl


def test_time_calibrate_tree_with_simple_tree():

    alifestd_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[1]", "[none]", "[1]", "[2]", "[2]"],
            "branch_length": [8, 0, 2, 1, 11],
            "name": ["A", "B", "C", "D", "E"],
        }
    )
    leaf_node_origin_times = {3: 52, 4: 62}  # 3 -> "D", 4 -> "E"

    for df in alifestd_df, alifestd_df.sample(frac=1):
        df_ = df.copy()
        calibrated_df = impl.time_calibrate_tree(df, leaf_node_origin_times)

        assert df.equals(df_)
        assert ip.popsingleton(alifestd_find_root_ids(calibrated_df)) == 0
        assert dict(
            zip(calibrated_df["name"], calibrated_df["origin_time"])
        ) == {
            "E": 62,
            "D": 52,
            "C": 51,
            "B": 49,
            "A": 41,
        }


def test_time_calibrate_tree_with_empty_tree():
    alifestd_df = pd.DataFrame(
        {
            "id": [],
            "ancestor_list": [],
            "branch_length": [],
            "name": [],
        }
    )
    alifestd_df_ = alifestd_df.copy()
    leaf_node_origin_times = {}
    calibrated_df = impl.time_calibrate_tree(
        alifestd_df, leaf_node_origin_times
    )
    assert calibrated_df.equals(alifestd_df_)
    assert alifestd_df.equals(alifestd_df_)


def test_time_calibrate_tree_with_singleton():
    alifestd_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
            "branch_length": [0],
            "name": ["Q"],
        }
    )
    leaf_node_origin_times = {0: 42}  # 0 -> "Q"

    expected_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
            "ancestor_id": [0],
            "origin_time": [42],
            "name": ["Q"],
        }
    )

    alifestd_df_ = alifestd_df.copy()
    calibrated_df = impl.time_calibrate_tree(
        alifestd_df, leaf_node_origin_times
    )
    assert calibrated_df.sort_index(axis="columns").equals(
        expected_df.sort_index(axis="columns")
    )
    assert alifestd_df.equals(alifestd_df_)


def test_time_calibrate_tree_with_disjoint_tree1():
    alifestd_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": ["[1]", "[none]", "[1]", "[2]", "[2]", "[none]"],
            "branch_length": [8, 0, 2, 1, 11, 99],
            "name": ["A", "B", "C", "D", "E", "Q"],
        }
    )
    leaf_node_origin_times = {3: 52, 4: 62, 5: 11}  # 3->D, 4->E, 5->Q

    for df in alifestd_df, alifestd_df.sample(frac=1):
        df_ = df.copy()
        calibrated_df = impl.time_calibrate_tree(df, leaf_node_origin_times)

        assert df.equals(df_)
        assert set(alifestd_find_root_ids(calibrated_df)) == {0, 5}
        assert dict(
            zip(calibrated_df["name"], calibrated_df["origin_time"])
        ) == {
            "E": 62,
            "D": 52,
            "C": 51,
            "B": 49,
            "A": 41,
            "Q": 11,
        }


def test_time_calibrate_tree_with_disjoint_tree2():
    alifestd_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[1]",
                "[none]",
                "[1]",
                "[2]",
                "[2]",
                "[none]",
                "[5]",
            ],
            "branch_length": [8, 0, 2, 1, 11, 0, 1],
            "name": ["A", "B", "C", "D", "E", "Q", "R"],
        }
    )
    leaf_node_origin_times = {3: 52, 4: 62, 6: 1}  # 3->D, 4->E, 6->R,

    for df in alifestd_df, alifestd_df.sample(frac=1):
        df_ = df.copy()
        calibrated_df = impl.time_calibrate_tree(df, leaf_node_origin_times)

        assert df.equals(df_)
        assert set(alifestd_find_root_ids(calibrated_df)) == {0, 5}
        assert dict(
            zip(calibrated_df["name"], calibrated_df["origin_time"])
        ) == {
            "E": 62,
            "D": 52,
            "C": 51,
            "B": 49,
            "A": 41,
            "Q": 0,
            "R": 1,
        }


def test_time_calibrate_tree_with_disjoint_tree3():
    alifestd_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[1]",
                "[none]",
                "[1]",
                "[2]",
                "[2]",
                "[6]",
                "[none]",
            ],
            "branch_length": [8, 0, 2, 1, 11, 1, 0],
            "name": ["A", "B", "C", "D", "E", "Q", "R"],
        }
    )
    leaf_node_origin_times = {3: 52, 4: 62, 6: 1}  # 3->D, 4->E, 6->R,

    for df in alifestd_df, alifestd_df.sample(frac=1):
        df_ = df.copy()
        calibrated_df = impl.time_calibrate_tree(df, leaf_node_origin_times)

        assert df.equals(df_)
        assert set(alifestd_find_root_ids(calibrated_df)) == {0, 5}
        assert dict(
            zip(calibrated_df["name"], calibrated_df["origin_time"])
        ) == {
            "E": 62,
            "D": 52,
            "C": 51,
            "B": 49,
            "A": 41,
            "Q": 0,
            "R": 1,
        }


def test_time_calibrate_tree_with_zero_length_branch_tree():

    alifestd_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[1]", "[none]", "[1]", "[2]", "[2]"],
            "branch_length": [8, 0, 2, 1, 0],
            "name": ["A", "B", "C", "D", "E"],
        }
    )
    leaf_node_origin_times = {3: 52, 4: 51}  # 3 -> "D", 4 -> "E"

    for df in alifestd_df, alifestd_df.sample(frac=1):
        df_ = df.copy()
        calibrated_df = impl.time_calibrate_tree(df, leaf_node_origin_times)

        assert df.equals(df_)
        assert ip.popsingleton(alifestd_find_root_ids(calibrated_df)) == 0
        assert dict(
            zip(calibrated_df["name"], calibrated_df["origin_time"])
        ) == {
            "E": 51,
            "D": 52,
            "C": 51,
            "B": 49,
            "A": 41,
        }
