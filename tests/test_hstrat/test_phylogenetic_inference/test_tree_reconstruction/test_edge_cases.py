from hstrat import hstrat
from hstrat.phylogenetic_inference import tree_reconstruction
from Bio.Phylo.TreeConstruction import DistanceMatrix, BaseTree

from _SimpleGenomeAnnotatedWithDenseRetention import (
    SimpleGenomeAnnotatedWithDenseRetention,
)

import random
import warnings

from alifedata_phyloinformatics_convert import biopython_tree_to_alife_dataframe, alife_dataframe_to_dendropy_tree

from dendropy.calculate.treecompare import symmetric_difference
from dendropy import TaxonNamespace, Tree

import pytest

def tree_difference(x, y):
    tree_a = alife_dataframe_to_dendropy_tree(biopython_tree_to_alife_dataframe(x))
    tree_b = alife_dataframe_to_dendropy_tree(biopython_tree_to_alife_dataframe(y))

    common_namespace = TaxonNamespace()
    tree_a.migrate_taxon_namespace(common_namespace)
    tree_b.migrate_taxon_namespace(common_namespace)

    tree_a.encode_bipartitions()
    for bp in tree_a.bipartition_encoding:
        bp.is_mutable = False
    tree_b.encode_bipartitions()
    for bp in tree_b.bipartition_encoding:
        bp.is_mutable = False

    return symmetric_difference(
        tree_a,
        tree_b,
        is_bipartitions_updated=True
    )

def test_empty_population():
    population = []
    distance_matrix = tree_reconstruction.calculate_distance_matrix(population)

    compare(distance_matrix, DistanceMatrix(names=[], matrix=[]))

    tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    assert tree_difference(tree, BaseTree.Tree()) == 0.0


def test_singleton_population():
    organism = hstrat.HereditaryStratigraphicColumn(
        # retain strata from every generation
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(1)
    )
    for _ in range(100):
        organism.DepositStratum()

    population = [organism]
    names=["foo"]

    distance_matrix = tree_reconstruction.calculate_distance_matrix(
        population, names=names
    )

    compare(
        distance_matrix,
        DistanceMatrix(
            names=names,
            matrix=[[0]]
        )
    )
    tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    assert tree_difference(tree, BaseTree.Tree(rooted=False)) == 0.0

def test_dual_population_no_mrca():
    organism1 = SimpleGenomeAnnotatedWithDenseRetention()
    organism2 = SimpleGenomeAnnotatedWithDenseRetention()

    for _ in range(100):
        organism1.annotation.DepositStratum()
        organism2.annotation.DepositStratum()

    population = [organism1, organism2]
    names=["foo", "bar"]

    # make sure calculate_distance_matrix emmits a warning
    with pytest.warns(UserWarning):
        distance_matrix = tree_reconstruction.calculate_distance_matrix(
            population, names=names
        )

    compare(
        distance_matrix,
        DistanceMatrix(
            names=names,
            matrix=[
                [0],
                [0, 0]
            ]
        )
    )
    tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    root_clade = BaseTree.Clade(name='Inner')
    root_clade.clades = [
        BaseTree.Clade(branch_length=0.0, name='bar'),
        BaseTree.Clade(branch_length=0.0, name='foo')
    ]
    true_tree = BaseTree.Tree(rooted=False, root=root_clade)

    assert tree_difference(tree, true_tree) == 0.0


def test_dual_population_with_mrca():
    organism1 = SimpleGenomeAnnotatedWithDenseRetention()
    organism2 = SimpleGenomeAnnotatedWithDenseRetention()

    population = [organism1, organism2]
    names=["foo", "bar"]

    for _ in range(100):
        parents = random.choices(population, k=len(population))
        population = [parent.CreateOffspring() for parent in parents]

    # make sure calculate_distance_matrix does not emmit a warning
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        distance_matrix = tree_reconstruction.calculate_distance_matrix(
            population, names=names
        )

    compare(
        distance_matrix,
        DistanceMatrix(
            names=names,
            matrix=[
                [0],
                [2.5, 0]
            ]
        )
    )
    tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    root_clade = BaseTree.Clade(name='Inner')
    root_clade.clades = [
        BaseTree.Clade(branch_length=1.25, name='bar'),
        BaseTree.Clade(branch_length=1.25, name='foo')
    ]
    true_tree = BaseTree.Tree(rooted=False, root=root_clade)

    assert tree_difference(tree, true_tree) == 0.0
