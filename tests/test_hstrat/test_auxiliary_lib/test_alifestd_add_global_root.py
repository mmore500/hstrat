import warnings

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_add_global_root,
    alifestd_find_root_ids,
    alifestd_make_empty,
    alifestd_validate,
)


def test_empty():
    res = alifestd_add_global_root(alifestd_make_empty())
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [False, True])
def test_single_root_ancestor_list(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 4
    assert alifestd_validate(result_df)

    root_ids = alifestd_find_root_ids(result_df)
    assert len(root_ids) == 1

    new_root_id = result_df["id"].max()
    assert new_root_id == 3
    root_row = result_df[result_df["id"] == new_root_id].iloc[0]
    assert root_row["ancestor_list"] == "[none]"

    # Old root should now point to new root
    old_root = result_df[result_df["id"] == 0].iloc[0]
    assert old_root["ancestor_list"] == f"[{new_root_id}]"

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_single_root_ancestor_id(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 0],
            "ancestor_list": ["[none]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 4
    assert alifestd_validate(result_df)

    new_root_id = result_df["id"].max()
    assert new_root_id == 3

    root_row = result_df[result_df["id"] == new_root_id].iloc[0]
    assert root_row["ancestor_id"] == new_root_id
    assert root_row["ancestor_list"] == "[none]"

    # Old root should now point to new root
    old_root = result_df[result_df["id"] == 0].iloc[0]
    assert old_root["ancestor_id"] == new_root_id
    assert old_root["ancestor_list"] == f"[{new_root_id}]"

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_multiple_roots(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[none]", "[0]", "[none]", "[2]"],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 5
    assert alifestd_validate(result_df)

    root_ids = alifestd_find_root_ids(result_df)
    assert len(root_ids) == 1

    new_root_id = result_df["id"].max()
    assert new_root_id == 4

    # Both old roots should point to new root
    old_root_0 = result_df[result_df["id"] == 0].iloc[0]
    old_root_2 = result_df[result_df["id"] == 2].iloc[0]
    assert old_root_0["ancestor_list"] == f"[{new_root_id}]"
    assert old_root_2["ancestor_list"] == f"[{new_root_id}]"

    # Non-root nodes should be unchanged
    node_1 = result_df[result_df["id"] == 1].iloc[0]
    node_3 = result_df[result_df["id"] == 3].iloc[0]
    assert node_1["ancestor_list"] == "[0]"
    assert node_3["ancestor_list"] == "[2]"

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_multiple_roots_ancestor_id(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 2, 2],
            "ancestor_list": ["[none]", "[0]", "[none]", "[2]"],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 5
    assert alifestd_validate(result_df)

    new_root_id = result_df["id"].max()

    old_root_0 = result_df[result_df["id"] == 0].iloc[0]
    old_root_2 = result_df[result_df["id"] == 2].iloc[0]
    assert old_root_0["ancestor_id"] == new_root_id
    assert old_root_2["ancestor_id"] == new_root_id

    # Non-root nodes unchanged
    node_1 = result_df[result_df["id"] == 1].iloc[0]
    assert node_1["ancestor_id"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_ancestor_id_only(mutate: bool):
    """Test with ancestor_id but no ancestor_list column."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 0],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 4
    assert "ancestor_list" not in result_df.columns

    new_root_id = result_df["id"].max()
    assert new_root_id == 3

    root_row = result_df[result_df["id"] == new_root_id].iloc[0]
    assert root_row["ancestor_id"] == new_root_id

    # Old root should now point to new root
    old_root = result_df[result_df["id"] == 0].iloc[0]
    assert old_root["ancestor_id"] == new_root_id

    # Non-root nodes unchanged
    node_1 = result_df[result_df["id"] == 1].iloc[0]
    assert node_1["ancestor_id"] == 0
    node_2 = result_df[result_df["id"] == 2].iloc[0]
    assert node_2["ancestor_id"] == 0

    root_ids = alifestd_find_root_ids(result_df)
    assert len(root_ids) == 1
    assert root_ids[0] == new_root_id

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_ancestor_id_only_multiple_roots(mutate: bool):
    """Test ancestor_id only with multiple roots."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 2, 2],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 5

    new_root_id = result_df["id"].max()

    # Both old roots should point to new root
    old_root_0 = result_df[result_df["id"] == 0].iloc[0]
    old_root_2 = result_df[result_df["id"] == 2].iloc[0]
    assert old_root_0["ancestor_id"] == new_root_id
    assert old_root_2["ancestor_id"] == new_root_id

    # Non-root nodes unchanged
    node_1 = result_df[result_df["id"] == 1].iloc[0]
    node_3 = result_df[result_df["id"] == 3].iloc[0]
    assert node_1["ancestor_id"] == 0
    assert node_3["ancestor_id"] == 2

    root_ids = alifestd_find_root_ids(result_df)
    assert len(root_ids) == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_sexual_ancestor_list(mutate: bool):
    """Test with sexual phylogeny (multiple ancestors in ancestor_list)."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[none]", "[none]", "[0,1]", "[0,1]"],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 5

    new_root_id = result_df["id"].max()
    assert new_root_id == 4

    # Old roots should point to new root
    old_root_0 = result_df[result_df["id"] == 0].iloc[0]
    old_root_1 = result_df[result_df["id"] == 1].iloc[0]
    assert old_root_0["ancestor_list"] == f"[{new_root_id}]"
    assert old_root_1["ancestor_list"] == f"[{new_root_id}]"

    # Sexual nodes should be unchanged
    node_2 = result_df[result_df["id"] == 2].iloc[0]
    node_3 = result_df[result_df["id"] == 3].iloc[0]
    assert node_2["ancestor_list"] == "[0,1]"
    assert node_3["ancestor_list"] == "[0,1]"

    # New root is valid
    root_row = result_df[result_df["id"] == new_root_id].iloc[0]
    assert root_row["ancestor_list"] == "[none]"

    root_ids = alifestd_find_root_ids(result_df)
    assert len(root_ids) == 1
    assert root_ids[0] == new_root_id

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_sexual_ancestor_list_single_root(mutate: bool):
    """Test sexual phylogeny with a single root."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[none]", "[0]", "[0]", "[1,2]"],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 5

    new_root_id = result_df["id"].max()

    # Old root should point to new root
    old_root = result_df[result_df["id"] == 0].iloc[0]
    assert old_root["ancestor_list"] == f"[{new_root_id}]"

    # Sexual node should be unchanged
    node_3 = result_df[result_df["id"] == 3].iloc[0]
    assert node_3["ancestor_list"] == "[1,2]"

    # Non-root asexual nodes unchanged
    node_1 = result_df[result_df["id"] == 1].iloc[0]
    assert node_1["ancestor_list"] == "[0]"

    root_ids = alifestd_find_root_ids(result_df)
    assert len(root_ids) == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_sexual_with_empty_bracket_roots(mutate: bool):
    """Test sexual phylogeny where roots use [] instead of [none]."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[]", "[0]", "[0,1]"],
        }
    )

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 4

    new_root_id = result_df["id"].max()

    old_root = result_df[result_df["id"] == 0].iloc[0]
    assert old_root["ancestor_list"] == f"[{new_root_id}]"

    # Sexual node unchanged
    node_2 = result_df[result_df["id"] == 2].iloc[0]
    assert node_2["ancestor_list"] == "[0,1]"


@pytest.mark.parametrize("mutate", [False, True])
def test_root_attrs_origin_time(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "origin_time": [10, 20],
        }
    )

    result_df = alifestd_add_global_root(
        phylogeny_df, mutate=mutate, root_attrs={"origin_time": 5},
    )

    assert len(result_df) == 3
    new_root_id = result_df["id"].max()
    root_row = result_df[result_df["id"] == new_root_id].iloc[0]
    assert root_row["origin_time"] == 5


@pytest.mark.parametrize("mutate", [False, True])
def test_root_attrs_new_column(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
        }
    )

    result_df = alifestd_add_global_root(
        phylogeny_df, mutate=mutate, root_attrs={"origin_time": 5},
    )

    assert len(result_df) == 3
    new_root_id = result_df["id"].max()
    root_row = result_df[result_df["id"] == new_root_id].iloc[0]
    assert root_row["origin_time"] == 5


@pytest.mark.parametrize("mutate", [False, True])
def test_root_attrs_multiple(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "origin_time": [10, 20],
            "taxon_label": ["A", "B"],
        }
    )

    result_df = alifestd_add_global_root(
        phylogeny_df,
        mutate=mutate,
        root_attrs={"origin_time": 0, "taxon_label": "root"},
    )

    assert len(result_df) == 3
    new_root_id = result_df["id"].max()
    root_row = result_df[result_df["id"] == new_root_id].iloc[0]
    assert root_row["origin_time"] == 0
    assert root_row["taxon_label"] == "root"


@pytest.mark.parametrize("mutate", [False, True])
def test_root_attrs_empty(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
        }
    )

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 3
    assert "origin_time" not in result_df.columns


@pytest.mark.parametrize("mutate", [False, True])
def test_root_attrs_empty_with_existing_column(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "origin_time": [10, 20],
        }
    )

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 3
    new_root_id = result_df["id"].max()
    root_row = result_df[result_df["id"] == new_root_id].iloc[0]
    # origin_time not in root_attrs, so NaN from concat
    assert pd.isna(root_row["origin_time"])


def test_warns_on_branch_length_columns():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "branch_length": [0.0, 1.0],
        }
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_add_global_root(phylogeny_df)
        assert len(w) == 1
        assert "branch_length" in str(w[0].message)


def test_warns_on_edge_length_columns():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "edge_length": [0.0, 1.0],
        }
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_add_global_root(phylogeny_df)
        assert len(w) == 1
        assert "edge_length" in str(w[0].message)


def test_warns_on_origin_time_delta():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "origin_time_delta": [0.0, 1.0],
        }
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_add_global_root(phylogeny_df)
        assert len(w) == 1
        assert "origin_time_delta" in str(w[0].message)


def test_warns_on_node_depth():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "node_depth": [0, 1],
        }
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_add_global_root(phylogeny_df)
        assert len(w) == 1
        assert "node_depth" in str(w[0].message)


def test_warns_on_multiple_columns():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "branch_length": [0.0, 1.0],
            "edge_length": [0.0, 1.0],
            "num_descendants": [1, 0],
        }
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_add_global_root(phylogeny_df)
        assert len(w) == 1
        msg = str(w[0].message)
        assert "branch_length" in msg
        assert "edge_length" in msg
        assert "num_descendants" in msg


def test_no_warning_without_warned_columns():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
        }
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_add_global_root(phylogeny_df)
        assert len(w) == 0


@pytest.mark.parametrize("mutate", [False, True])
def test_new_root_has_only_applicable_columns(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_id": [0, 0],
            "ancestor_list": ["[none]", "[0]"],
            "origin_time": [0, 1],
            "taxon_label": ["A", "B"],
            "some_extra_col": [42, 99],
        }
    )

    result_df = alifestd_add_global_root(
        phylogeny_df, mutate=mutate, root_attrs={"origin_time": 0},
    )

    new_root_id = result_df["id"].max()
    root_row = result_df[result_df["id"] == new_root_id].iloc[0]

    # These should be set
    assert root_row["id"] == new_root_id
    assert root_row["ancestor_id"] == new_root_id
    assert root_row["ancestor_list"] == "[none]"
    assert root_row["origin_time"] == 0

    # These should be NaN
    assert pd.isna(root_row["taxon_label"])
    assert pd.isna(root_row["some_extra_col"])


@pytest.mark.parametrize("mutate", [False, True])
def test_noncontiguous_ids(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [5, 10, 15],
            "ancestor_id": [5, 5, 10],
            "ancestor_list": ["[none]", "[5]", "[10]"],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 4
    assert alifestd_validate(result_df)

    new_root_id = result_df["id"].max()
    assert new_root_id == 16

    root_ids = alifestd_find_root_ids(result_df)
    assert len(root_ids) == 1
    assert root_ids[0] == new_root_id

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_ancestor_list_only(mutate: bool):
    """Test with ancestor_list but no ancestor_id column."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[none]"],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 4
    assert alifestd_validate(result_df)
    assert "ancestor_id" not in result_df.columns

    new_root_id = result_df["id"].max()
    root_row = result_df[result_df["id"] == new_root_id].iloc[0]
    assert root_row["ancestor_list"] == "[none]"

    root_ids = alifestd_find_root_ids(result_df)
    assert len(root_ids) == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
def test_single_node(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "ancestor_list": ["[none]"],
        }
    )
    original_df = phylogeny_df.copy()

    result_df = alifestd_add_global_root(phylogeny_df, mutate=mutate)

    assert len(result_df) == 2
    assert alifestd_validate(result_df)

    new_root_id = result_df["id"].max()
    assert new_root_id == 1

    root_ids = alifestd_find_root_ids(result_df)
    assert len(root_ids) == 1
    assert root_ids[0] == new_root_id

    if not mutate:
        assert original_df.equals(phylogeny_df)
