import typing
from enum import Enum
from typing import Iterable
from collections import namedtuple

import numpy as np
import opytional as opyt

from ...._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    argsort,
    give_len,
    jit,
)
from ._TrieInnerNode import TrieInnerNode
from ._TrieLeafNode import TrieLeafNode


class MatrixColumn(Enum):
    ID = 0
    PARENT_ID = 1
    FIRST_CHILD_ID = 2
    LAST_CHILD_ID = 3
    NEXT_SIBLING_ID = 4
    RANK = 5
    DIFFERENTIA = 6
    TAXON_LABEL_ID = 7
    IS_LEAF_NODE = 8


# not currently used right now
def _get_np_uint_by_size(
    bit_width: int,
) -> typing.Type:  # todo expand to union
    """Determines the smallest possible integer to store stratigraphic data."""
    sizes = [np.uint8, np.uint16, np.uint32]
    for i in range(3, 6):
        if bit_width < 2**i:
            return sizes[i - 3]
    return np.uint64


@jit()
def _add_child_matrix(m: np.ndarray, root_index: int, child_index: int) -> int:
    """Adds a child to the matrix and returns the index of the child."""
    if m[root_index][MatrixColumn.LAST_CHILD_ID.value]:
        m[m[root_index][MatrixColumn.LAST_CHILD_ID.value]][
            MatrixColumn.NEXT_SIBLING_ID.value
        ] = child_index
    else:
        m[root_index][MatrixColumn.FIRST_CHILD_ID.value] = child_index
    m[root_index][MatrixColumn.LAST_CHILD_ID.value] = child_index
    return child_index


# NOTE: THIS ENTIRE FUNCTION USES ONE-INDEXING FOR IDS TO LEAVE 0 AS A PLACEHOLDER
@jit()
def build_trie_from_artifacts_matrix(
    ranks: np.ndarray,
    differentia: np.ndarray,
    stratum_differentia_bit_width: int,
    taxon_label_ids: typing.List[int],
) -> np.ndarray:
    """
    Implementation of below function build_trie_from_artifacts using
    a matrix rather than the TrieInnerNode.
    It is designed to work with the optimized case in which the
    evolution was perfectly synchronous, so it, presently, cannot
    work with a population out-of-sync in terms of ranks.
    Better suited for optimization with Numba.
    """
    m = np.zeros(
        (differentia.shape[1]+1, 9),
        dtype=np.uint64,  # _get_np_uint_by_size(stratum_differentia_bit_width),
    )  # assumes all bit widths the same
    assert 2**stratum_differentia_bit_width > len(taxon_label_ids)

    curr_index = 0

    def step_index() -> int:
        """
        Steps the current index of the most recent node and returns the value.
        Additionally resizes the matrix if needed.
        """
        nonlocal curr_index, m
        if curr_index >= m.shape[0] - 2:
            m = np.vstack((m, np.zeros((m.shape[0], 9), dtype=m.dtype)))
        curr_index += 1
        return curr_index

    m[curr_index] = np.array([step_index()] + [0] * 8)  # root inner node
    for label, artifact_idx in zip(
        taxon_label_ids, range(differentia.shape[1])
    ):
        root_index = 1

        # todo: are rank comparisons really needed here ?
        for allele_idx in range(ranks.shape[0]):
            rank = ranks[allele_idx]
            diff = differentia[allele_idx][artifact_idx]

            # iterate through the children of the node checking for a match to branch off of
            create_new = True
            child_index = m[int(root_index)][MatrixColumn.FIRST_CHILD_ID.value]
            while child_index:
                if m[child_index][MatrixColumn.DIFFERENTIA.value] == diff:
                    root_index = child_index
                    create_new = False
                    break
                child_index = m[child_index][
                    MatrixColumn.NEXT_SIBLING_ID.value
                ]

            # create a new inner node for the new branch
            if create_new:
                m[curr_index] = np.array(
                    [
                        step_index(),
                        root_index,
                        0,
                        0,
                        0,
                        rank,
                        diff,
                        0,
                        0,
                    ]
                )
                root_index = _add_child_matrix(m, int(root_index), curr_index)

        m[int(curr_index)] = np.array(
            [
                step_index(),
                int(root_index),
                0,
                0,
                0,
                0,
                0,
                label,
                1,
            ]
        )

        root_index = _add_child_matrix(m, int(root_index), curr_index)

    return m[: curr_index + 1]  # todo: check if we need a .copy()?


def build_trie_from_artifacts_progressive(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[Iterable],
) -> TrieInnerNode:

    taxon_labels = list(taxon_labels or [*map(str, range(len(population)))])
    root = TrieInnerNode()
    differentiae: Iterable[Iterable[int]] = zip(
        *(x.IterRetainedDifferentia() for x in population)
    )
    ranks: Iterable[int] = population[0].IterRetainedRanks()
    alleles: list[tuple[int, Iterable[int]]] = [*zip(ranks, differentiae)]

    def recursive_builder(
        root: TrieInnerNode, stage: int, target_artifacts: set[int]
    ) -> None:
        rank, diff = alleles[stage]
        unique_d = {}
        for i, d in filter(
            lambda x: x[0] in target_artifacts, enumerate(diff)
        ):
            if d not in unique_d:
                unique_d[d] = set()
            unique_d[d].add(i)
        if stage < len(alleles) - 1:
            for d, targets in unique_d.items():
                recursive_builder(
                    TrieInnerNode(rank=rank, differentia=d, parent=root),
                    stage + 1,
                    targets,
                )
        else:
            for d, targets in unique_d.items():
                parent = TrieInnerNode(rank=rank, differentia=d, parent=root)
                for i in targets:
                    TrieLeafNode(taxon_label=taxon_labels[i], parent=parent)

    recursive_builder(root, 0, {*range(len(population))})
    return root


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

        if is_perfectly_synchronous:
            root.InsertTaxon(label, artifact.IterRankDifferentiaZip())
        else:
            res = root.GetDeepestCongruousAlleleOrigination(
                artifact.IterRankDifferentiaZip(copyable=True)
            )
            node, subsequent_allele_genesis_iter = res
            node.InsertTaxon(label, subsequent_allele_genesis_iter)

    return root
