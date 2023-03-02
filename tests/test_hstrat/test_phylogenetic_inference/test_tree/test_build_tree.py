import itertools as it
import os
import random
import warnings

from Bio.Phylo.TreeConstruction import BaseTree, DistanceMatrix
import _impl as impl
import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import pytest

from hstrat import hstrat

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "version_pin",
    [hstrat.__version__],
)
def test_empty_population(version_pin):
    population = []
    tree = hstrat.build_tree(
        [],
        version_pin=version_pin,
    )

    assert (
        impl.tree_distance_metric(
            tree,
            BaseTree.Tree(),
        )
        == 0.0
    )


@pytest.mark.parametrize(
    "version_pin",
    [hstrat.__version__],
)
def test_dual_population_no_mrca(version_pin):
    organism1 = hstrat.HereditaryStratigraphicColumn().CloneNthDescendant(100)
    organism2 = hstrat.HereditaryStratigraphicColumn().CloneNthDescendant(100)

    population = [organism1, organism2]
    names = ["foo", "bar"]

    with pytest.raises(ValueError):
        tree = hstrat.build_tree(population, version_pin, taxon_labels=names)

    tree = hstrat.build_tree(
        population, version_pin, taxon_labels=names, force_common_ancestry=True
    )

    root_clade = BaseTree.Clade(name="Inner1")
    root_clade.clades = [
        BaseTree.Clade(branch_length=101.0, name="bar"),
        BaseTree.Clade(branch_length=101.0, name="foo"),
    ]
    true_tree = BaseTree.Tree(rooted=False, root=root_clade)

    assert (
        impl.tree_distance_metric(
            apc.alife_dataframe_to_biopython_tree(tree), true_tree
        )
        == 0.0
    )


@pytest.mark.parametrize(
    "version_pin",
    [hstrat.__version__],
)
def test_dual_population_with_mrca(version_pin):
    organism1 = hstrat.HereditaryStratigraphicColumn()
    organism2 = hstrat.HereditaryStratigraphicColumn()

    population = [organism1, organism2]
    names = ["foo", "bar"]

    for _ in range(100):
        parents = random.choices(population, k=len(population))
        population = [parent.CloneDescendant() for parent in parents]

    tree = hstrat.build_tree(
        population, version_pin=version_pin, taxon_labels=names
    )

    root_clade = BaseTree.Clade(name="Inner")
    root_clade.clades = [
        BaseTree.Clade(branch_length=0.0, name="bar"),
        BaseTree.Clade(branch_length=0.0, name="foo"),
    ]
    true_tree = BaseTree.Tree(rooted=False, root=root_clade)

    assert (
        impl.tree_distance_metric(
            apc.alife_dataframe_to_biopython_tree(tree),
            true_tree,
        )
        == 0.0
    )


@pytest.mark.parametrize(
    "version_pin",
    [hstrat.__version__],
)
@pytest.mark.parametrize(
    "orig_tree",
    [
        impl.setup_dendropy_tree(f"{assets_path}/grandchild_and_aunt.newick"),
        impl.setup_dendropy_tree(
            f"{assets_path}/grandchild_and_auntuncle.newick"
        ),
        # TODO: handle this edge case
        # impl.setup_dendropy_tree(
        #     f"{assets_path}/grandchild.newick"
        # ),
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
        # TODO: handle this edge case
        # impl.setup_dendropy_tree(
        #     f"{assets_path}/justroot.newick"
        # ),
        impl.setup_dendropy_tree(f"{assets_path}/triplets.newick"),
        impl.setup_dendropy_tree(f"{assets_path}/twins.newick"),
    ],
)
def test_handwritten_trees(version_pin, orig_tree):
    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn().CloneNthDescendant(
            10
        ),
    )

    reconst_df = hstrat.build_tree(extant_population, hstrat.__version__)
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
        assert (
            abs(
                original_distance_matrix.distance(a, b)
                - reconstructed_distance_matrix.distance(a, b)
            )
            < 2.0
        )

    assert impl.tree_distance_metric(orig_tree, reconst_tree) < 2.0


@pytest.mark.parametrize(
    "orig_tree",
    [
        # TODO
        # pytest.param(
        #     impl.setup_dendropy_tree(f"{assets_path}/nk_ecoeaselection.csv"),
        #     marks=pytest.mark.heavy,
        # ),
        # impl.setup_dendropy_tree(f"{assets_path}/nk_lexicaseselection.csv"),
        impl.setup_dendropy_tree(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
# @pytest.mark.parametrize(
#     "retention_policy",
#     [
#       TODO
#     ]
# )
def test_reconstructed_mrca(orig_tree):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn().CloneNthDescendant(
            num_depositions
        ),
    )

    reconst_df = hstrat.build_tree(extant_population, hstrat.__version__)
    reconst_tree = apc.alife_dataframe_to_dendropy_tree(
        reconst_df,
        setup_edge_lengths=True,
    )
    pdm = reconst_tree.phylogenetic_distance_matrix()

    assert len(list(reconst_tree.leaf_node_iter())) == len(extant_population)
    assert [
        leaf_node.distance_from_root()
        for leaf_node in reconst_tree.leaf_node_iter()
    ] == [
        extant_col.GetNumStrataDeposited() - 1
        for extant_col in extant_population
    ]

    for reconst_node_pair, extant_column_pair in zip(
        it.combinations(reconst_tree.leaf_node_iter(), 2),
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

    first_reconst = hstrat.build_tree_upgma(
        extant_population, estimator, prior
    )
    for rep in range(3):
        second_reconst = hstrat.build_tree_upgma(
            [wrap(col) for col in extant_population],
            estimator,
            prior,
        )
        assert first_reconst.equals(second_reconst)
