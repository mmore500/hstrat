import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_try_add_ancestor_id_col,
    alifestd_validate,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_aggregate_phylogenies(
            [
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
                ),
                pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
            ]
        ),
        alifestd_aggregate_phylogenies(
            [
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
                )[0:1],
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
                )[0:1],
            ]
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        )[-1:0],
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        )[0:1],
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        alifestd_aggregate_phylogenies(
            [
                pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
            ]
        ),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny-empty-list-notation.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny-noncompact1.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny-noncompact2.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny-uniq.csv"
        ),
    ],
)
@pytest.mark.parametrize(
    "apply_combine",
    [
        lambda x: alifestd_aggregate_phylogenies(
            [
                x,
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
                ),
            ]
        ),
        lambda x: x,
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_try_add_ancestor_id_col,
        lambda x: x.sample(frac=1),
        lambda x: alifestd_try_add_ancestor_id_col(x.sample(frac=1)),
        lambda x: x,
    ],
)
def test_valid_asexual(phylogeny_df, apply_combine, apply):
    phylogeny_df = apply(apply_combine(phylogeny_df.copy()))

    phylogeny_df_ = phylogeny_df.copy()
    assert alifestd_validate(phylogeny_df)
    assert phylogeny_df_.equals(phylogeny_df)


@pytest.mark.parametrize(
    "phylogeny_path",
    [
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-missing-id-column.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-ancestor_list-syntax1.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-ancestor_list-syntax2.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-ancestor_list-syntax3.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-ancestor_list-syntax4.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-duplicate-id1.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-duplicate-id2.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-duplicate-id3.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-mismatched-ancestor_id-ancestor_list-columns1.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-mismatched-ancestor_id-ancestor_list-columns2.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-mismatched-ancestor_id-ancestor_list-columns3.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-missing-ancestor_list-column1.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-missing-ancestor_list-column2.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-negative-id1.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-negative-id2.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-negative-id3.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-nonexistant-ancestor_id-id1.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-nonexistant-ancestor_id-id2.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-nonexistant-ancestor_id-id3.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-nonexistant-ancestor_id-id4.csv",
        f"{assets_path}/example-standard-toy-asexual-phylogeny--invalid-nonexistant-ancestor_list-id.csv",
    ],
)
@pytest.mark.parametrize(
    "apply_combine",
    [
        lambda x: pd.concat(
            [
                x,
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-asexual-phylogeny-uniq.csv"
                ),
            ]
        ),
        lambda x: x,
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_try_add_ancestor_id_col,
        lambda x: x.sample(frac=1),
        lambda x: alifestd_try_add_ancestor_id_col(x.sample(frac=1)),
        lambda x: x,
    ],
)
def test_invalid_asexual(phylogeny_path, apply_combine, apply):
    phylogeny_df = apply_combine(pd.read_csv(phylogeny_path))
    try:
        phylogeny_df = apply(phylogeny_df)
    except Exception:
        pass

    phylogeny_df_ = phylogeny_df.copy()
    assert not alifestd_validate(phylogeny_df)
    assert phylogeny_df_.equals(phylogeny_df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        )[0:2],
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny-empty-list-notation.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny-noncompact1.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny-noncompact2.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny-uniq.csv"
        ),
    ],
)
@pytest.mark.parametrize(
    "apply_combine",
    [
        lambda x: alifestd_aggregate_phylogenies(
            [
                x,
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
                ),
            ]
        ),
        lambda x: alifestd_aggregate_phylogenies(
            [
                x,
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
                ),
            ]
        ),
        lambda x: x,
    ],
)
@pytest.mark.parametrize(
    "apply_shuffle",
    [
        lambda x: x.sample(frac=1),
        lambda x: x,
    ],
)
def test_valid_sexual(phylogeny_df, apply_combine, apply_shuffle):
    phylogeny_df = apply_shuffle(apply_combine(phylogeny_df.copy()))

    phylogeny_df_ = phylogeny_df.copy()
    assert alifestd_validate(phylogeny_df)
    assert phylogeny_df_.equals(phylogeny_df)


@pytest.mark.parametrize(
    "phylogeny_path",
    [
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-missing-id-column.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-ancestor_list-syntax1.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-ancestor_list-syntax2.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-ancestor_list-syntax3.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-ancestor_list-syntax4.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-duplicate-id1.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-duplicate-id2.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-duplicate-id3.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-mismatched-ancestor_id-ancestor_list-columns1.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-mismatched-ancestor_id-ancestor_list-columns2.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-negative-id1.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-negative-id2.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-negative-id3.csv",
        f"{assets_path}/example-standard-toy-sexual-phylogeny--invalid-nonexistant-ancestor_list-id.csv",
    ],
)
@pytest.mark.parametrize(
    "apply_combine",
    [
        lambda x: pd.concat(
            [
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-asexual-phylogeny-uniq.csv"
                ),
                x,
            ]
        ),
        lambda x: pd.concat(
            [
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-sexual-phylogeny-uniq.csv"
                ),
                x,
            ]
        ),
        lambda x: x,
    ],
)
@pytest.mark.parametrize(
    "apply_shuffle",
    [
        lambda x: x.sample(frac=1),
        lambda x: x,
    ],
)
def test_invalid_sexual(phylogeny_path, apply_combine, apply_shuffle):
    phylogeny_df = apply_shuffle(apply_combine(pd.read_csv(phylogeny_path)))

    phylogeny_df_ = phylogeny_df.copy()
    assert not alifestd_validate(phylogeny_df)
    assert phylogeny_df_.equals(phylogeny_df)


def test_empty():
    empty1 = pd.DataFrame(
        {
            "ancestor_list": [],
            "id": [],
        }
    )
    assert alifestd_validate(empty1)

    empty2 = pd.DataFrame(
        {
            "ancestor_list": [],
            "id": [],
            "origin_time": [],
        }
    )
    assert alifestd_validate(empty2)
