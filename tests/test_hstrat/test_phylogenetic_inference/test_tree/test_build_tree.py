import itertools as it
import os
import random

from Bio.Phylo.TreeConstruction import BaseTree
import alifedata_phyloinformatics_convert as apc
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import alifestd_validate

assets_path = os.path.join(os.path.dirname(__file__), "assets")

from . import _impl as impl


@pytest.mark.parametrize(
    "version_pin",
    [hstrat.__version__],
)
def test_empty_population(version_pin):
    population = []
    tree = hstrat.build_tree(
        population,
        version_pin=version_pin,
    )

    assert len(tree) == 0
    assert alifestd_validate(tree)


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
    assert alifestd_validate(tree)
    tree.loc[:, "name"] = tree["taxon_label"]

    root_clade = BaseTree.Clade(name="Inner1")
    root_clade.clades = [
        BaseTree.Clade(branch_length=101.0, name="bar"),
        BaseTree.Clade(branch_length=101.0, name="foo"),
    ]
    true_tree = BaseTree.Tree(rooted=False, root=root_clade)

    assert (
        impl.tree_unweighted_robinson_foulds_distance(
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
    assert alifestd_validate(tree)
    tree["name"] = tree["taxon_label"]

    root_clade = BaseTree.Clade(name="Inner")
    root_clade.clades = [
        BaseTree.Clade(branch_length=0.0, name="bar"),
        BaseTree.Clade(branch_length=0.0, name="foo"),
    ]
    true_tree = BaseTree.Tree(rooted=False, root=root_clade)

    assert (
        impl.tree_unweighted_robinson_foulds_distance(
            apc.alife_dataframe_to_biopython_tree(tree),
            true_tree,
        )
        == 0.0
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
        hstrat.fixed_resolution_algo.Policy(3),
        hstrat.recency_proportional_resolution_algo.Policy(3),
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

    reconst_df = hstrat.build_tree(extant_population, hstrat.__version__)
    reconst_tree = apc.alife_dataframe_to_dendropy_tree(
        reconst_df,
        setup_edge_lengths=True,
    )
    pdm = reconst_tree.phylogenetic_distance_matrix()

    sorted_leaf_nodes = sorted(
        reconst_tree.leaf_node_iter(), key=lambda x: int(x.taxon.label)
    )
    assert len(sorted_leaf_nodes) == len(extant_population)
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
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        hstrat.col_to_specimen,
    ],
)
@pytest.mark.parametrize(
    "version_pin",
    [hstrat.__version__],
)
def test_determinism(orig_tree, retention_policy, wrap, version_pin):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )

    first_reconst = hstrat.build_tree(extant_population, version_pin)
    for _rep in range(3):
        _ = _rep
        second_reconst = hstrat.build_tree(
            [wrap(col) for col in extant_population], version_pin
        )
        assert first_reconst.equals(second_reconst)


@pytest.mark.parametrize(
    "version_pin",
    [hstrat.__version__],
)
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
def test_reconstructed_taxon_labels(version_pin, orig_tree, retention_policy):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )
    taxon_labels = [str(id(x)) for x in extant_population]

    reconst_df = hstrat.build_tree(
        extant_population,
        version_pin,
        taxon_labels=taxon_labels,
    )
    assert "taxon_label" in reconst_df
    assert set(taxon_labels) < set(reconst_df["taxon_label"])

    reconst_df = hstrat.build_tree(
        extant_population,
        version_pin,
    )
    assert "taxon_label" in reconst_df
    assert len(reconst_df["taxon_label"].unique()) == len(
        reconst_df["taxon_label"]
    )
    assert set(map(str, range(len(extant_population)))) < set(
        reconst_df["taxon_label"]
    )
