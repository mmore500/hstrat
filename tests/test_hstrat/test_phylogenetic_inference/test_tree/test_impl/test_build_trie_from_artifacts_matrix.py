import pytest

import numpy as np

from hstrat import hstrat
from hstrat.phylogenetic_inference.tree._impl._build_trie_from_artifacts import (
    build_trie_from_artifacts,
    build_trie_from_artifacts_matrix,
)
from .._impl._simulate_evolution import Genome, simulate_evolution
from .._impl._is_matrix_equal_trie import is_matrix_equal_trie


# tests for method accuracy are outside. therefore, in this function
# we can compare the other methods against the method that is being
# tested in other tests to make sure everything is right
@pytest.mark.parametrize(
    "synchronous",
    [True, pytest.param(False, marks=pytest.mark.heavy)]
)
@pytest.mark.parametrize(
    "generations",
    [1, 4, 20, pytest.param(100, marks=pytest.mark.heavy)]
)
@pytest.mark.parametrize(
    "carrying_capacity",
    [25, 100]
)
def test_build_trie_matrix(
    synchronous: bool,
    generations: int,
    carrying_capacity: int
) -> None:

    start_pop = [Genome()]
    evolved = simulate_evolution(
        start_pop, generations=generations, carrying_capacity=carrying_capacity
    )
    extant_population = [x.annotation for x in evolved]

    root = build_trie_from_artifacts(
        extant_population,
        [str(i) for i in range(len(evolved))],
        False,
        lambda x: x,
    )

    assemblage = hstrat.pop_to_assemblage(extant_population)
    ranks = assemblage._assemblage_df.index.to_numpy().astype(np.uint64)
    differentia = assemblage._assemblage_df.to_numpy().astype(np.uint64)
    m = build_trie_from_artifacts_matrix(
        ranks,
        differentia,
        extant_population[0]._stratum_differentia_bit_width,
        [*range(len(evolved))],
    )

    assert is_matrix_equal_trie(m, root)


def test_build_trie_matrix_empty():
    m = build_trie_from_artifacts_matrix(np.zeros((0,)), np.zeros((0, 0)), 8, [0])
    root = build_trie_from_artifacts([], [], False, lambda x: x)
    assert is_matrix_equal_trie(m, root)


