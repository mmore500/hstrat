import gc
import typing

import opytional as opyt

from ...._auxiliary_lib import (
    AnyTreeFastLeafIter,
    HereditaryStratigraphicArtifact,
    argsort,
    give_len,
)
from ._TrieInnerNode import TrieInnerNode
from ._TrieLeafNode import TrieLeafNode


def build_trie_from_artifacts(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[typing.Iterable],
    force_common_ancestry: bool,
    progress_wrap: typing.Callable,
) -> TrieInnerNode:
    """Implementation detail for build_tree_trie_ensemble.

    See `build_tree_trie` for parameter descriptions.
    """
    taxon_labels = list(
        opyt.or_value(
            taxon_labels,
            map(str, range(len(population))),
        )
    )

    root = TrieInnerNode(rank=None, differentia=None)

    sort_order = argsort([x.GetNumStrataDeposited() for x in population])
    sorted_labels = [taxon_labels[i] for i in sort_order]
    sorted_population = [population[i] for i in sort_order]
    for label, artifact in progress_wrap(
        give_len(zip(sorted_labels, sorted_population), len(population))
    ):

        root.InsertTaxon(label, artifact.IterRankDifferentiaZip())

    # hacky way to iterate over all TrieInnerNodes...
    objs = filter(lambda x: isinstance(x, TrieInnerNode), gc.get_objects())
    # sort by tiebreaker to ensure deterministic behavior
    for obj in sorted(objs, key=lambda x: x._tiebreaker):
        # reset tree from "search" configuration to "build" configuration
        if obj.parent is not obj._buildparent:
            obj.parent = None
            obj.parent = obj._buildparent

    # no inner nodes should be leaves...
    assert not any (
        isinstance(leaf, TrieInnerNode)
        for leaf in AnyTreeFastLeafIter(root)
    )

    return root
