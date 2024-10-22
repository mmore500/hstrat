import random
from string import ascii_letters

import pytest

from hstrat.phylogenetic_inference.tree._impl._build_trie_from_artifacts import (
    build_trie_from_artifacts,
    build_trie_from_artifacts_progressive
)
from .._impl._simulate_evolution import Genome, simulate_evolution

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
def test_build_trie_progressive(
    synchronous: bool,
    generations: int,
    carrying_capacity: int
) -> None:

    start_pop = [Genome()]
    evolved = simulate_evolution(
        start_pop, generations=generations, carrying_capacity=carrying_capacity
    )
    extant_population = [x.annotation for x in evolved]

    taxon_labels = [''.join(random.choices(ascii_letters, k=10)) for _ in extant_population]
    assert build_trie_from_artifacts(
        extant_population,
        taxon_labels,
        False,
        lambda x: x,
    ) == build_trie_from_artifacts_progressive(
        extant_population, taxon_labels, multiprocess=False
    )


def test_build_trie_progressive_empty():
    assert build_trie_from_artifacts(
        [], [], False, lambda x: x
    ) == build_trie_from_artifacts_progressive(
        [], [], multiprocess=False
    )
