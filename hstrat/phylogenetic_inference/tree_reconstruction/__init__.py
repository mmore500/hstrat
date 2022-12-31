"""Functions to reconstruct a phylogenetic tree from extant hereditary strata."""

__all__ = []

from ..._auxiliary_lib import launder_impl_modules as _launder

from itertools import combinations
from typing import Iterable

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from warnings import warn

from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
import numpy as np

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ..pairwise import (
    _calc_rank_of_earliest_detectable_mrca_between,
    _calc_ranks_since_mrca_bounds_with,
    _does_definitively_have_no_common_ancestor,
)


def _to_tril(matrix):
    return [
        row[:row_idx] + [0.0] for row_idx, row in enumerate(matrix.tolist())
    ]


def distance_matrix_helper(x, y):
    mrca_bounds = _calc_ranks_since_mrca_bounds_with(x, y)
    if mrca_bounds is not None:
        mrca_lb, mrca_ub = mrca_bounds
    earliest_detectable_mrca = _calc_rank_of_earliest_detectable_mrca_between(
        x, y
    )

    if mrca_bounds is None:
        if earliest_detectable_mrca:
            return (earliest_detectable_mrca - 1) / 2
        else:
            return min(x, y) / 2

    if _does_definitively_have_no_common_ancestor(x, y):
        warn(
            f"""No common ancestor exists between {x} and {y}; returning a distance of 0.
            This behavior may change in the future (i.e., by returning two distinct trees.)
            """,
        )
        return 0

    return (mrca_lb + mrca_ub - 1) / 2


def calculate_distance_matrix(
    population: Iterable[HereditaryStratigraphicColumn],
):
    matrix_data = np.zeros(len(population), len(population))

    pairwise = combinations(list(len(population)), 2)

    for a, b in pairwise:
        matrix_data[a][b] = sum(
            distance_matrix_helper(x, y)
            for x, y in zip(population[a], population[b])
        )

    return DistanceMatrix(
        names=[str(x) for x in population], matrix=_to_tril(matrix_data.T)
    )


def reconstruct_tree(
    distance_matrix: DistanceMatrix, algo: Literal["nj", "upgma"] = "nj"
):
    return getattr(DistanceTreeConstructor(), algo)(distance_matrix)

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
