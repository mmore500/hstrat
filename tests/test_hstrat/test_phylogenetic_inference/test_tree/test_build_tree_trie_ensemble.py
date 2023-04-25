import os

import pytest

from hstrat import hstrat

from . import _impl as impl

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "orig_tree",
    [
        pytest.param(
            impl.setup_dendropy_tree(f"{assets_path}/nk_ecoeaselection.csv"),
            marks=pytest.mark.heavy,
        ),
        impl.setup_dendropy_tree(f"{assets_path}/nk_lexicaseselection.csv"),
        impl.setup_dendropy_tree(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.recency_proportional_resolution_algo.Policy(3),
        hstrat.fixed_resolution_algo.Policy(5),
    ],
)
def test_postprocessing_consistency(orig_tree, retention_policy):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
            stratum_differentia_bit_width=1,
        ).CloneNthDescendant(num_depositions),
    )

    nop_df, rb_df1, rb_df2 = hstrat.build_tree_trie_ensemble(
        extant_population,
        trie_postprocessors=[
            lambda x, **kwargs: x,
            hstrat.SampleAncestralRollbacksTriePostprocessor(seed=1),
            hstrat.SampleAncestralRollbacksTriePostprocessor(seed=1),
        ],
    )

    assert not nop_df.equals(rb_df1)
    assert rb_df1.equals(rb_df2)
