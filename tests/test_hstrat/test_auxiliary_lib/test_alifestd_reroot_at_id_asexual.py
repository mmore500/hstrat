import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import (
    alifestd_reroot_at_id_asexual,
    alifestd_validate,
)


def test_alifestd_reroot_at_id_asexual_inner_node_terminal_node():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [3, 3, 4, 4, 5, 5],
            "ancestor_list": ["[3]", "[3]", "[4]", "[4]", "[5]", "[none]"],
        }
    )
    assert alifestd_validate(phylogeny_df)
    reroot_at = 1
    expected_result = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [3, 1, 4, 1, 3, 4],
            "ancestor_list": ["[3]", "[none]", "[4]", "[1]", "[3]", "[4]"],
        }
    )

    for df in (phylogeny_df, phylogeny_df.sample(frac=1)):
        df_ = df.copy()
        result = alifestd_reroot_at_id_asexual(df, reroot_at)

        assert expected_result.equals(result.sort_index())
        assert df.equals(df_)


def test_alifestd_reroot_at_id_asexual_inner_node_bifurcation():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [1, 3, 4, 4, 4, 1],
            "ancestor_list": ["[1]", "[3]", "[4]", "[4]", "[none]", "[1]"],
        }
    )
    assert alifestd_validate(phylogeny_df)
    reroot_at = 1
    expected_result = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [1, 1, 4, 1, 3, 1],
            "ancestor_list": ["[1]", "[none]", "[4]", "[1]", "[3]", "[1]"],
        }
    )

    for df in (phylogeny_df, phylogeny_df.sample(frac=1)):
        df_ = df.copy()
        result = alifestd_reroot_at_id_asexual(df, reroot_at)

        assert expected_result.equals(result.sort_index())
        assert df.equals(df_)


def test_alifestd_reroot_at_id_asexual_inner_node_trifurcation():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [1, 3, 1, 4, 4, 1],
            "ancestor_list": ["[1]", "[3]", "[1]", "[4]", "[none]", "[1]"],
        }
    )
    assert alifestd_validate(phylogeny_df)
    reroot_at = 1
    expected_result = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [1, 1, 1, 1, 3, 1],
            "ancestor_list": ["[1]", "[none]", "[1]", "[1]", "[3]", "[1]"],
        }
    )

    for df in (phylogeny_df, phylogeny_df.sample(frac=1)):
        df_ = df.copy()
        result = alifestd_reroot_at_id_asexual(df, reroot_at)

        assert expected_result.equals(result.sort_index())
        assert df.equals(df_)


def test_alifestd_reroot_at_id_asexual_singleton():
    phylogeny_df = pd.DataFrame(
        {
            "id": [7],
            "ancestor_id": [7],
            "ancestor_list": "[none]",
        }
    )
    reroot_at = 7
    expected_result = phylogeny_df

    df_ = phylogeny_df.copy()
    result = alifestd_reroot_at_id_asexual(phylogeny_df, reroot_at)
    assert np.array_equal(expected_result, result)
    assert phylogeny_df.equals(df_)
