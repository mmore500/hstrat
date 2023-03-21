import os

import alifedata_phyloinformatics_convert as apc
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import alifestd_validate

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
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        hstrat.col_to_specimen,
    ],
)
@pytest.mark.parametrize(
    "estimator",
    [
        "maximum_likelihood",
        "unbiased",
    ],
)
@pytest.mark.parametrize(
    "prior",
    [
        "arbitrary",
        "uniform",
        hstrat.ExponentialPrior(1.01),
    ],
)
def test_determinism(orig_tree, retention_policy, wrap, estimator, prior):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )

    first_reconst = hstrat.build_tree_nj(extant_population, estimator, prior)
    for _rep in range(3):
        _ = _rep
        second_reconst = hstrat.build_tree_nj(
            [wrap(col) for col in extant_population],
            estimator,
            prior,
        )
        assert first_reconst.equals(second_reconst)


@pytest.mark.parametrize(
    "orig_tree",
    [
        impl.setup_dendropy_tree(f"{assets_path}/nk_lexicaseselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.recency_proportional_resolution_algo.Policy(4),
    ],
)
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        hstrat.col_to_specimen,
    ],
)
def test_reconstructed_taxon_labels(orig_tree, retention_policy, wrap):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )
    taxon_labels = [str(id(x)) for x in extant_population]

    reconst_df = hstrat.build_tree_nj(
        [*map(wrap, extant_population)],
        "maximum_likelihood",
        "arbitrary",
        taxon_labels=taxon_labels,
        negative_origin_time_correction_method="shift",
    )
    assert "taxon_label" in reconst_df
    assert set(taxon_labels) < set(reconst_df["taxon_label"])

    reconst_df = hstrat.build_tree_nj(
        [*map(wrap, extant_population)],
        "maximum_likelihood",
        "arbitrary",
        negative_origin_time_correction_method="shift",
    )
    assert "taxon_label" in reconst_df
    assert len(reconst_df["taxon_label"].unique()) == len(
        reconst_df["taxon_label"]
    )
    assert set(map(str, range(len(extant_population)))) < set(
        reconst_df["taxon_label"]
    )


@pytest.mark.parametrize(
    "orig_tree",
    [
        impl.setup_dendropy_tree(f"{assets_path}/nk_ecoeaselection.csv"),
        impl.setup_dendropy_tree(f"{assets_path}/nk_lexicaseselection.csv"),
        # nj flunks building this tree with quartet distance 1.0
        # over all retention policies
        # upgma flunks too (but build_tree_trie doesn't)
        # impl.setup_dendropy_tree(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(2),
        hstrat.recency_proportional_resolution_algo.Policy(2),
    ],
)
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        hstrat.col_to_specimen,
    ],
)
def test_reconstructed_dist(orig_tree, retention_policy, wrap):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )

    reconst_df = hstrat.build_tree_nj(
        [wrap(col) for col in extant_population],
        "maximum_likelihood",
        "arbitrary",
        taxon_labels=(leaf.taxon.label for leaf in orig_tree.leaf_node_iter()),
    )
    assert "origin_time" in reconst_df

    assert alifestd_validate(reconst_df)
    reconst_tree = apc.alife_dataframe_to_dendropy_tree(
        reconst_df,
        setup_edge_lengths=True,
    )

    assert len(list(reconst_tree.leaf_node_iter())) == len(extant_population)
    sorted_leaf_nodes = sorted(
        reconst_tree.leaf_node_iter(), key=lambda x: int(x.taxon.label)
    )
    assert {
        int(leaf_node.distance_from_root()) for leaf_node in sorted_leaf_nodes
    } == {
        extant_col.GetNumStrataDeposited() - 1
        for extant_col in extant_population
    }
    assert sorted(
        int(leaf_node.distance_from_root()) for leaf_node in sorted_leaf_nodes
    ) == sorted(
        extant_col.GetNumStrataDeposited() - 1
        for extant_col in extant_population
    )
    assert [
        int(leaf_node.distance_from_root()) for leaf_node in sorted_leaf_nodes
    ] == [
        extant_col.GetNumStrataDeposited() - 1
        for extant_col in extant_population
    ]

    reconstruction_error = impl.tree_quartet_distance(
        orig_tree,
        reconst_tree,
    )
    # arbitrary threshold...  quartet dist expectations: random 0.75, worst 1.0
    assert 0.0 <= reconstruction_error < 0.4
