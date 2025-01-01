import itertools as it
import os
import random

from Bio.Phylo.TreeConstruction import BaseTree
import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import networkx as nx
import pandas as pd
import pytest
from tqdm import tqdm

from hstrat import hstrat
from hstrat._auxiliary_lib import (
    alifestd_collapse_unifurcations,
    alifestd_has_multiple_roots,
    alifestd_is_chronologically_ordered,
    alifestd_validate,
    generate_n,
    random_tree,
    seed_random,
)
from hstrat.phylogenetic_inference.tree._impl import (
    build_tree_searchtable_python,
)

from .. import _impl as impl

assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")


def test_empty_population():
    population = []
    tree = build_tree_searchtable_python(
        population,
    )

    assert len(tree) == 0
    assert alifestd_validate(tree)
    assert alifestd_is_chronologically_ordered(tree)


def test_dual_population_no_mrca():
    organism1 = hstrat.HereditaryStratigraphicColumn().CloneNthDescendant(100)
    organism2 = hstrat.HereditaryStratigraphicColumn().CloneNthDescendant(100)

    population = [organism1, organism2]
    names = ["foo", "bar"]

    with pytest.raises(ValueError):
        tree = build_tree_searchtable_python(
            population,
            taxon_labels=names,
        )

    tree = build_tree_searchtable_python(
        population,
        taxon_labels=names,
        force_common_ancestry=True,
    )
    tree["name"] = tree["taxon_label"]
    assert not alifestd_has_multiple_roots(tree)
    assert alifestd_validate(tree)
    assert alifestd_is_chronologically_ordered(tree)

    root_clade = BaseTree.Clade(name="Inner1")
    root_clade.clades = [
        BaseTree.Clade(branch_length=100.0, name="bar"),
        BaseTree.Clade(branch_length=100.0, name="foo"),
    ]
    true_tree = BaseTree.Tree(rooted=False, root=root_clade)
    assert (
        impl.tree_unweighted_robinson_foulds_distance(
            apc.alife_dataframe_to_biopython_tree(
                alifestd_collapse_unifurcations(tree),
                setup_branch_lengths=True,
            ),
            true_tree,
        )
        == 0.0
    )


@pytest.mark.parametrize(
    "orig_tree",
    [
        impl.setup_dendropy_tree(f"{assets_path}/grandchild_and_aunt.newick"),
        impl.setup_dendropy_tree(
            f"{assets_path}/grandchild_and_auntuncle.newick"
        ),
        impl.setup_dendropy_tree(f"{assets_path}/grandchild.newick"),
        impl.setup_dendropy_tree(
            f"{assets_path}/grandtriplets_and_aunt.newick"
        ),
        impl.setup_dendropy_tree(
            f"{assets_path}/grandtriplets_and_auntuncle.newick"
        ),
        impl.setup_dendropy_tree(f"{assets_path}/grandtriplets.newick"),
        impl.setup_dendropy_tree(f"{assets_path}/grandtwins_and_aunt.newick"),
        impl.setup_dendropy_tree(
            f"{assets_path}/grandtwins_and_auntuncle.newick"
        ),
        impl.setup_dendropy_tree(f"{assets_path}/grandtwins.newick"),
        impl.setup_dendropy_tree(f"{assets_path}/justroot.newick"),
        impl.setup_dendropy_tree(f"{assets_path}/triplets.newick"),
        impl.setup_dendropy_tree(f"{assets_path}/twins.newick"),
    ],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
    ],
)
@pytest.mark.parametrize("wrap", [lambda x: x, hstrat.col_to_specimen])
def test_handwritten_trees(orig_tree, retention_policy, wrap):
    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(10),
    )

    reconst_df = build_tree_searchtable_python(
        [*map(wrap, extant_population)],
    )

    assert alifestd_validate(reconst_df)
    assert alifestd_is_chronologically_ordered(reconst_df)
    reconst_tree = apc.alife_dataframe_to_dendropy_tree(
        reconst_df,
        setup_edge_lengths=True,
    )
    reconst_tree.collapse_unweighted_edges()

    common_namespace = dp.TaxonNamespace()
    orig_tree.migrate_taxon_namespace(common_namespace)
    reconst_tree.migrate_taxon_namespace(common_namespace)

    original_distance_matrix = orig_tree.phylogenetic_distance_matrix()
    reconstructed_distance_matrix = reconst_tree.phylogenetic_distance_matrix()

    taxa = [node.taxon for node in orig_tree.leaf_node_iter()]

    for a, b in it.combinations(taxa, 2):
        assert original_distance_matrix.distance(
            a, b
        ) == reconstructed_distance_matrix.distance(a, b)


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
def test_reconstructed_mrca(orig_tree, retention_policy):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )

    reconst_df = build_tree_searchtable_python(
        extant_population,
    )
    assert "origin_time" in reconst_df

    assert alifestd_validate(reconst_df)
    assert alifestd_is_chronologically_ordered(reconst_df)
    reconst_tree = apc.alife_dataframe_to_dendropy_tree(
        reconst_df,
        setup_edge_lengths=True,
    )
    pdm = reconst_tree.phylogenetic_distance_matrix()

    assert len(list(reconst_tree.leaf_node_iter())) == len(extant_population)
    sorted_leaf_nodes = sorted(
        reconst_tree.leaf_node_iter(), key=lambda x: int(x.taxon.label)
    )
    assert {
        leaf_node.distance_from_root() for leaf_node in sorted_leaf_nodes
    } == {
        extant_col.GetNumStrataDeposited() - 1
        for extant_col in extant_population
    }
    assert sorted(
        leaf_node.distance_from_root() for leaf_node in sorted_leaf_nodes
    ) == sorted(
        extant_col.GetNumStrataDeposited() - 1
        for extant_col in extant_population
    )
    assert [
        leaf_node.distance_from_root() for leaf_node in sorted_leaf_nodes
    ] == [
        extant_col.GetNumStrataDeposited() - 1
        for extant_col in extant_population
    ]

    for reconst_node_pair, extant_column_pair in zip(
        it.combinations(sorted_leaf_nodes, 2),
        it.combinations(extant_population, 2),
    ):
        reconst_mrca = impl.descend_unifurcations(
            pdm.mrca(*map(lambda x: x.taxon, reconst_node_pair))
        )

        (
            lower_mrca_bound,
            upper_mrca_bound,
        ) = hstrat.calc_rank_of_mrca_bounds_between(
            *extant_column_pair, prior="arbitrary"
        )

        assert (
            lower_mrca_bound
            <= reconst_mrca.distance_from_root()
            < upper_mrca_bound
        )


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
def test_col_specimen_consistency(orig_tree, retention_policy):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )

    reconst_df1 = build_tree_searchtable_python(
        extant_population,
    )
    reconst_df2 = build_tree_searchtable_python(
        [hstrat.col_to_specimen(col) for col in extant_population],
    )

    assert reconst_df1[["id", "ancestor_list"]].equals(
        reconst_df2[["id", "ancestor_list"]]
    )


@pytest.mark.parametrize("tree_size", [10, 30, 100, 300, 1000])
@pytest.mark.parametrize(
    "differentia_width", [1, pytest.param(2, marks=pytest.mark.heavy), 8, 64]
)
@pytest.mark.parametrize(
    "tree_seed",
    [*range(10)]
    + [pytest.param(i, marks=pytest.mark.heavy) for i in range(10, 100)],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.recency_proportional_resolution_algo.Policy(1),
        pytest.param(
            hstrat.recency_proportional_resolution_algo.Policy(2),
            marks=pytest.mark.heavy,
        ),
        pytest.param(
            hstrat.recency_proportional_resolution_algo.Policy(10),
            marks=pytest.mark.heavy,
        ),
        hstrat.fixed_resolution_algo.Policy(2),
    ],
)
@pytest.mark.parametrize(
    "exhaustive_check",
    [pytest.param(True, marks=pytest.mark.heavy), False],
)
def test_reconstructed_mrca_fuzz(
    tree_seed, tree_size, differentia_width, retention_policy, exhaustive_check
):

    seed_random(tree_seed)
    nx_tree = random_tree(n=tree_size, seed=tree_seed, create_using=nx.DiGraph)

    extant_population = hstrat.descend_template_phylogeny_networkx(
        nx_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
            stratum_differentia_bit_width=differentia_width,
        ),
    )

    reconst_df = build_tree_searchtable_python(
        extant_population,
        progress_wrap=tqdm,
    )
    assert "origin_time" in reconst_df

    assert alifestd_validate(reconst_df)
    assert alifestd_is_chronologically_ordered(reconst_df)
    reconst_tree = apc.alife_dataframe_to_dendropy_tree(
        reconst_df,
        setup_edge_lengths=True,
    )
    pdm = reconst_tree.phylogenetic_distance_matrix()

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

    for reconst_node_pair, extant_column_pair, label_pair in (
        (
            (
                (sorted_leaf_nodes[first_idx], sorted_leaf_nodes[second_idx]),
                (extant_population[first_idx], extant_population[second_idx]),
                (first_idx, second_idx),
            )
            for first_idx, second_idx in generate_n(
                lambda: (
                    random.randrange(len(extant_population)),
                    random.randrange(len(extant_population)),
                ),
                10000,
            )
        )
        if not exhaustive_check
        else zip(
            it.combinations(sorted_leaf_nodes, 2),
            it.combinations(extant_population, 2),
            it.combinations(range(len(extant_population)), 2),
        )
    ):
        reconst_mrca = impl.descend_unifurcations(
            pdm.mrca(*map(lambda x: x.taxon, reconst_node_pair))
        )

        (
            lower_mrca_bound,
            upper_mrca_bound,
        ) = hstrat.calc_rank_of_mrca_bounds_between(
            *extant_column_pair,
            prior="arbitrary",
            confidence_level=0.99999,
            strict=False,
        )

        if not (
            lower_mrca_bound
            <= reconst_mrca.distance_from_root()
            < upper_mrca_bound
        ):
            print(reconst_mrca.taxon.label)
            print(reconst_mrca.distance_from_root())
            print()
            for i, (col, ln) in enumerate(
                zip(extant_population, sorted_leaf_nodes)
            ):
                print()
                print("label", i)
                print(ln.distance_from_root())
                print(id(col))
                print(hstrat.col_to_ascii(col))
            print(nx.forest_str(nx_tree))
            print(reconst_tree.as_ascii_plot(plot_metric="length"))

        assert (
            lower_mrca_bound
            <= reconst_mrca.distance_from_root()
            < upper_mrca_bound
        ), (
            label_pair[0],
            label_pair[1],
            id(extant_column_pair[0]),
            id(extant_column_pair[1]),
            lower_mrca_bound,
            reconst_mrca.distance_from_root(),
            upper_mrca_bound,
        )


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
    "differentia_width",
    [
        1,
        8,
        64,
    ],
)
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        hstrat.col_to_specimen,
    ],
)
def test_determinism(orig_tree, retention_policy, differentia_width, wrap):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )

    first_reconst = build_tree_searchtable_python(
        extant_population,
    )
    for _rep in range(10):
        _ = _rep
        second_reconst = build_tree_searchtable_python(
            [wrap(col) for col in extant_population],
        )
        pd.testing.assert_frame_equal(first_reconst, second_reconst)


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

    reconst_df = build_tree_searchtable_python(
        [*map(wrap, extant_population)],
        taxon_labels=taxon_labels,
    )
    assert "taxon_label" in reconst_df
    assert set(taxon_labels) <= set(reconst_df["taxon_label"])

    reconst_df = build_tree_searchtable_python(
        [*map(wrap, extant_population)],
    )
    assert "taxon_label" in reconst_df
    assert set(map(str, range(len(extant_population)))) <= set(
        reconst_df["taxon_label"]
    )
