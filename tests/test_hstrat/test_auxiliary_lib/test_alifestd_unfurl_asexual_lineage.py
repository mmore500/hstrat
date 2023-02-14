import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import alifestd_unfurl_asexual_lineage


def test_alifestd_unfurl_asexual_lineage():
    phylogeny_df = pd.DataFrame({
        "id": [0, 1, 2, 3, 4, 5],
        "ancestor_id": [3, 3, 4, 4, 5, 5],
    })
    leaf_id = 1
    expected_result = np.array([1, 3, 4, 5])

    for df in phylogeny_df, phylogeny_df.sample(frac=1):
        df_ = df.copy()
        result = alifestd_unfurl_asexual_lineage(df, leaf_id)
        assert np.array_equal(expected_result, result)
        assert df.equals(df_)


def test_alifestd_unfurl_asexual_lineage_singleton():
    phylogeny_df = pd.DataFrame({
        "id": [7],
        "ancestor_id": [7],
    })
    leaf_id = 7
    expected_result = np.array([7])

    df_ = phylogeny_df.copy()
    result = alifestd_unfurl_asexual_lineage(phylogeny_df, leaf_id)
    assert np.array_equal(expected_result, result)
    assert phylogeny_df.equals(df_)
