import random
import warnings

from Bio.Phylo.TreeConstruction import BaseTree, DistanceMatrix
from _SimpleGenomeAnnotatedWithDenseRetention import (
    SimpleGenomeAnnotatedWithDenseRetention,
)
from aux_tree_tools import tree_difference
import pytest

from hstrat import hstrat
from hstrat.phylogenetic_inference import tree_reconstruction


def test_empty_population():
    population = []
    distance_matrix = tree_reconstruction.calculate_distance_matrix(population)

    assert str(distance_matrix) == str(DistanceMatrix(names=[], matrix=[]))

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
    names = ["foo"]

    distance_matrix = tree_reconstruction.calculate_distance_matrix(
        population, names=names
    )

    assert str(distance_matrix) == str(
        DistanceMatrix(names=names, matrix=[[0]])
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
    names = ["foo", "bar"]

    # make sure calculate_distance_matrix emmits a warning
    with pytest.warns(UserWarning):
        distance_matrix = tree_reconstruction.calculate_distance_matrix(
            [x.annotation for x in population], names=names
        )

    assert (
        str(distance_matrix),
        str(DistanceMatrix(names=names, matrix=[[0], [0, 0]])),
    )
    tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    root_clade = BaseTree.Clade(name="Inner")
    root_clade.clades = [
        BaseTree.Clade(branch_length=0.0, name="bar"),
        BaseTree.Clade(branch_length=0.0, name="foo"),
    ]
    true_tree = BaseTree.Tree(rooted=False, root=root_clade)

    assert tree_difference(tree, true_tree) == 0.0


def test_dual_population_with_mrca():
    organism1 = SimpleGenomeAnnotatedWithDenseRetention()
    organism2 = SimpleGenomeAnnotatedWithDenseRetention()

    population = [organism1, organism2]
    names = ["foo", "bar"]

    for _ in range(100):
        parents = random.choices(population, k=len(population))
        population = [parent.CreateOffspring() for parent in parents]

    # make sure calculate_distance_matrix does not emmit a warning
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        distance_matrix = tree_reconstruction.calculate_distance_matrix(
            [x.annotation for x in population], names=names
        )

    assert (
        str(distance_matrix),
        str(DistanceMatrix(names=names, matrix=[[0], [2.5, 0]])),
    )
    tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    root_clade = BaseTree.Clade(name="Inner")
    root_clade.clades = [
        BaseTree.Clade(branch_length=1.25, name="bar"),
        BaseTree.Clade(branch_length=1.25, name="foo"),
    ]
    true_tree = BaseTree.Tree(rooted=False, root=root_clade)

    assert tree_difference(tree, true_tree) == 0.0
