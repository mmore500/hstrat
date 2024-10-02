import typing
from enum import Enum
from collections import namedtuple

import numba
import numpy as np
import opytional as opyt

from ...._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    argsort,
    give_len,
)
from ._TrieInnerNode import TrieInnerNode


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


MatrixEntry = namedtuple("MatrixEntry", [
    'id', 'parent', 'first_child', 'last_child', 'next_sibling',
    'rank', 'differentia', 'taxon_label', 'is_leaf'
])


def _get_np_uint_by_size(bit_width: int) -> typing.Type:  # todo expand to union
    """ Determines the smallest possible integer to store stratigraphic data. """
    sizes = [np.uint8, np.uint16, np.uint32]
    for i in range(3, 6):
        if bit_width < 2 ** i:
            return sizes[i-3]
    return np.uint64


def _add_child_matrix(m: np.ndarray, root_index: int, child_index: int) -> int:
    """ Adds a child to the matrix and returns the index of the child. """
    if m[root_index][MatrixColumn.LAST_CHILD_ID.value]:
        m[m[root_index][MatrixColumn.LAST_CHILD_ID.value]][MatrixColumn.NEXT_SIBLING_ID.value] = child_index
    else:
        m[root_index][MatrixColumn.FIRST_CHILD_ID.value] = child_index
    m[root_index][MatrixColumn.LAST_CHILD_ID.value] = child_index
    return child_index

# NOTE: THIS ENTIRE FUNCTION USES ONE-INDEXING FOR IDS TO LEAVE 0 AS A PLACEHOLDER
# @numba.jit()
def build_trie_from_artifacts_matrix(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_label_ids: typing.List[int],
    progress_wrap: typing.Callable,
) -> np.ndarray:
    """
    Implementation of below function build_trie_from_artifacts using
    a matrix rather than the TrieInnerNode.
    Better suited for optimization with Numba.
    """

    m = np.zeros(
        (len(population), len(MatrixColumn)),
        dtype=_get_np_uint_by_size(population[0]._stratum_differentia_bit_width) # assumes all bit widths the same
    )
    assert 2**population[0]._stratum_differentia_bit_width > len(taxon_label_ids)

    curr_index = 0
    def step_index() -> int:
        """
        Steps the current index of the most recent node and returns the value.
        Additionally resizes the matrix if needed.
        """
        nonlocal curr_index, m
        if curr_index >= m.shape[0] - 2:
            m = np.vstack((m, np.zeros((m.shape[0], len(MatrixColumn)), dtype=m.dtype)))
        curr_index += 1
        return curr_index

    m[curr_index] = np.array([step_index()] + [0] * (len(MatrixColumn)-1))  # root inner node
    for label, artifact in progress_wrap(
        give_len(zip(taxon_label_ids, population), len(population))
    ):
        root_index = 1

        # todo: are rank comparisons really needed here ?
        for rank, differentia in artifact.IterRankDifferentiaZip():

            # iterate through the children of the node checking for a match to branch off of
            create_new = True
            if (child_index := m[root_index][MatrixColumn.FIRST_CHILD_ID.value]):
                while child_index:
                    if (
                        m[child_index][MatrixColumn.DIFFERENTIA.value] == differentia
                        and m[child_index][MatrixColumn.RANK.value] == rank
                    ):
                        root_index = child_index
                        create_new = False
                        break
                    child_index = m[child_index][MatrixColumn.NEXT_SIBLING_ID.value]

            # create a new inner node for the new branch
            if create_new:
                m[curr_index] = np.array(MatrixEntry(
                    id=step_index(), parent=root_index, first_child=0, last_child=0,
                    next_sibling=0, rank=rank, differentia=differentia, is_leaf=0, taxon_label=0
                ))
                root_index = _add_child_matrix(m, root_index, curr_index)

        # create a leaf node representing the inserted allele
        m[curr_index] = np.array(MatrixEntry(
            id=step_index(), parent=root_index, first_child=0, last_child=0, next_sibling=0,
            rank=0, differentia=0, taxon_label=label, is_leaf=1
        ))
        root_index = _add_child_matrix(m, root_index, curr_index)

    return m

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
