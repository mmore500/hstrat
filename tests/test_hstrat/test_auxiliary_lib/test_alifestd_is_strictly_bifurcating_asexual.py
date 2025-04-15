import pandas as pd

from hstrat._auxiliary_lib import alifestd_is_strictly_bifurcating_asexual


def test_valid_bifurcating_tree():
    df = pd.DataFrame({"id": [0, 1, 2], "ancestor_id": [0, 0, 0]})
    assert alifestd_is_strictly_bifurcating_asexual(df)


def test_invalid_tree_single_child1():
    df = pd.DataFrame({"id": [0, 1], "ancestor_id": [0, 0]})
    assert not alifestd_is_strictly_bifurcating_asexual(df)


def test_invalid_tree_single_child2():
    df = pd.DataFrame({"id": [0, 1, 2], "ancestor_id": [0, 0, 1]})
    assert not alifestd_is_strictly_bifurcating_asexual(df)


def test_invalid_tree_three_children1():
    df = pd.DataFrame({"id": [0, 1, 2, 3], "ancestor_id": [0, 0, 0, 0]})
    assert not alifestd_is_strictly_bifurcating_asexual(df)


def test_invalid_tree_three_children2():
    df = pd.DataFrame(
        {"id": [0, 1, 2, 3, 4, 5], "ancestor_id": [4, 0, 0, 0, 4, 4]}
    )
    assert not alifestd_is_strictly_bifurcating_asexual(df)


def test_invalid_tree_three_children3():
    df = pd.DataFrame({"id": [8, 1, 2, 3], "ancestor_id": [8, 8, 8, 8]})
    assert not alifestd_is_strictly_bifurcating_asexual(df)


def test_single_root():
    df = pd.DataFrame({"id": [0], "ancestor_id": [0]})
    assert alifestd_is_strictly_bifurcating_asexual(df)


def test_multiple_roots():
    df = pd.DataFrame({"id": [0, 1], "ancestor_id": [0, 1]})
    assert alifestd_is_strictly_bifurcating_asexual(df)


def test_mutate():
    df = pd.DataFrame({"id": [8, 1, 2, 3], "ancestor_id": [8, 8, 8, 8]})
    original_df = df.copy()
    alifestd_is_strictly_bifurcating_asexual(df)
    pd.testing.assert_frame_equal(df, original_df)
