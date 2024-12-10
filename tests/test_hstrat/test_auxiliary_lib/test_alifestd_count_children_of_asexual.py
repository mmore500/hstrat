import pandas as pd
import pytest

from hstrat._auxiliary_lib import alifestd_count_children_of_asexual


def sample_phylogeny_df1():
    """Fixture to provide a sample phylogeny dataframe."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "ancestor_id": [1, 1, 1, 2],
        },
    )


def sample_phylogeny_df2():
    """Fixture to provide a sample phylogeny dataframe."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "ancestor_list": ["[1]", "[1]", "[1]", "[2]"],
        },
    )


@pytest.mark.parametrize(
    "sample_phylogeny_df", [sample_phylogeny_df1(), sample_phylogeny_df2()]
)
def test_count_children_valid_parent(sample_phylogeny_df: pd.DataFrame):
    assert alifestd_count_children_of_asexual(sample_phylogeny_df, 1) == 2
    assert alifestd_count_children_of_asexual(sample_phylogeny_df, 2) == 1


@pytest.mark.parametrize(
    "sample_phylogeny_df", [sample_phylogeny_df1(), sample_phylogeny_df2()]
)
def test_count_children_no_children(sample_phylogeny_df: pd.DataFrame):
    assert alifestd_count_children_of_asexual(sample_phylogeny_df, 4) == 0
    assert alifestd_count_children_of_asexual(sample_phylogeny_df, 3) == 0


@pytest.mark.parametrize(
    "sample_phylogeny_df", [sample_phylogeny_df1(), sample_phylogeny_df2()]
)
def test_count_children_invalid_parent(sample_phylogeny_df: pd.DataFrame):
    with pytest.raises(ValueError):
        alifestd_count_children_of_asexual(sample_phylogeny_df, parent=999)


@pytest.mark.parametrize(
    "sample_phylogeny_df", [sample_phylogeny_df1(), sample_phylogeny_df2()]
)
def test_no_mutation_of_input(sample_phylogeny_df: pd.DataFrame):
    original_df = sample_phylogeny_df.copy()
    alifestd_count_children_of_asexual(
        sample_phylogeny_df, parent=1, mutate=False
    )
    pd.testing.assert_frame_equal(sample_phylogeny_df, original_df)
