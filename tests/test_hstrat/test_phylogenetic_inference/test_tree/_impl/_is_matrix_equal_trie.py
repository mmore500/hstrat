import numpy as np

from hstrat.phylogenetic_inference.tree._impl._TrieInnerNode import (
    TrieInnerNode,
)
from hstrat.phylogenetic_inference.tree._impl._build_trie_from_artifacts import (
    MatrixColumn,
)


def is_matrix_equal_trie(m: np.ndarray, root: TrieInnerNode) -> bool:
    # stack based approach to go through each root
    # the matrix approach should operate exactly the same as the normal one
    # therefore, the order in which children are added should be the same
    roots_to_analyze = [(root, 1)]
    while roots_to_analyze:
        r, i = roots_to_analyze.pop()
        if not (
            r.rank == m[i][MatrixColumn.RANK.value]
            and r.differentia == m[i][MatrixColumn.DIFFERENTIA.value]
        ):
            return False
        inner = [*r.inner_children]
        inner_m = []
        child_index = m[i][MatrixColumn.FIRST_CHILD_ID.value]
        while child_index:
            if m[child_index][MatrixColumn.IS_LEAF_NODE.value] == 0:
                inner_m.append(child_index)
            child_index = m[child_index][MatrixColumn.NEXT_SIBLING_ID.value]
        for a, b in zip(inner, inner_m):
            if not int(a.differentia) == m[b][MatrixColumn.DIFFERENTIA.value]:
                return False

        outer = [*r.outer_children]
        outer_m = []
        child_index = m[i][MatrixColumn.FIRST_CHILD_ID.value]
        while child_index:
            if m[child_index][MatrixColumn.IS_LEAF_NODE.value] == 1:
                outer_m.append(child_index)
            child_index = m[child_index][MatrixColumn.NEXT_SIBLING_ID.value]
        for a, b in zip(outer, outer_m):
            if (
                not int(a.taxon_label)
                == m[b][MatrixColumn.TAXON_LABEL_ID.value]
            ):
                return False

        roots_to_analyze.extend([*zip(inner, inner_m)])

    return True
