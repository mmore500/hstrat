import gc
import typing

import opytional as opyt

from ...._auxiliary_lib import (
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

    is_perfectly_synchronous = all(
        artifact.GetNumStrataDeposited()
        == population[0].GetNumStrataDeposited()
        for artifact in population
    )

    sort_order = argsort([x.GetNumStrataDeposited() for x in population])
    sorted_labels = [taxon_labels[i] for i in sort_order]
    sorted_population = [population[i] for i in sort_order]
    for label, artifact in progress_wrap(
        give_len(zip(sorted_labels, sorted_population), len(population))
    ):

        if True:
            root.InsertTaxon(label, artifact.IterRankDifferentiaZip())
        else:
            res = root.GetDeepestCongruousAlleleOrigination(
                artifact.IterRankDifferentiaZip(copyable=True)
            )
            node, subsequent_allele_genesis_iter = res
            node.InsertTaxon(label, subsequent_allele_genesis_iter)

    for obj in gc.get_objects():
        if isinstance(obj, (TrieInnerNode, TrieLeafNode)):
            obj.parent = obj._buildparent

    return root
