import itertools as it
import os
import typing

import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_validate,
)

from . import _impl as impl

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize("use_impl", ["cpp", "python", None])
def test_empty_population(use_impl: typing.Optional[str]):
    population = []
    tree = hstrat.build_tree_searchtable(population, use_impl=use_impl)

    assert len(tree) == 0
    assert alifestd_validate(tree)
    assert alifestd_is_chronologically_ordered(tree)


@pytest.mark.parametrize("use_impl", ["cpp", "python", None])
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
def test_smoke(
    use_impl: typing.Optional[str],
    orig_tree: dp.Tree,
    retention_policy: object,
    wrap: typing.Callable,
):
    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(10),
    )

    reconst_df = hstrat.build_tree_searchtable(
        [*map(wrap, extant_population)], use_impl=use_impl
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
        impl.setup_dendropy_tree(f"{assets_path}/grandchild_and_aunt.newick"),
    ],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
    ],
)
def test_bad_use_impl(orig_tree: dp.Tree, retention_policy: object):
    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(10),
    )

    with pytest.raises(ValueError):
        hstrat.build_tree_searchtable(extant_population, use_impl="foobar")
