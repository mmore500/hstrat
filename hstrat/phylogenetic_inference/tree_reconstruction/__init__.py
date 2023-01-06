"""Functions to reconstruct a phylogenetic tree from extant hereditary strata."""

__all__ = []

from itertools import combinations
from typing import Iterable, Any
from string import ascii_lowercase

from ..._auxiliary_lib import launder_impl_modules as _launder
from ..._auxiliary_lib import to_tril

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from warnings import warn

from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor, BaseTree
import numpy as np

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ..pairwise import (
    calc_rank_of_earliest_detectable_mrca_between,
    calc_ranks_since_mrca_bounds_with,
    does_definitively_have_no_common_ancestor,
)


def distance_matrix_helper(x, y):
    mrca_bounds = calc_ranks_since_mrca_bounds_with(x, y)
    if mrca_bounds is not None:
        mrca_lb, mrca_ub = mrca_bounds
    earliest_detectable_mrca = calc_rank_of_earliest_detectable_mrca_between(
        x, y
    )

    if mrca_bounds is not None:
        return (mrca_lb + mrca_ub - 1) / 2  # ub is exclusive

    if earliest_detectable_mrca is None:
        return min(x, y) / 2

    if earliest_detectable_mrca:
        return (earliest_detectable_mrca - 1) / 2

    if does_definitively_have_no_common_ancestor(x, y):
        assert earliest_detectable_mrca == 0
        warn(
            f"""No common ancestor exists between {x} and {y}; returning a distance of 0.
            This behavior may change in the future (i.e., by returning two distinct trees.)
            """,
        )
        return 0


def calculate_distance_matrix(
    population: Iterable[HereditaryStratigraphicColumn],
    names: Iterable[Any] = None
):
    matrix_data = np.zeros((len(population), len(population)))

    pairwise = combinations(range(len(population)), 2)

    for a, b in pairwise:
        matrix_data[a][b] = sum(
            distance_matrix_helper(x, y)
            for x, y in zip(population[a], population[b])
        )

    return DistanceMatrix(
        names=names if names else [*ascii_lowercase[: len(population)]],
        matrix=to_tril(matrix_data.T)
    )


def reconstruct_tree(
    distance_matrix: DistanceMatrix, algo: Literal["nj", "upgma"] = "nj"
):
    if algo not in ["nj", "upgma"]:
        raise ValueError(
            f"""Unsupported reconstruction algorithm {algo}. \
            Please choose one of 'nj', 'upgma'."""
        )
    if not distance_matrix:
        return BaseTree.Tree()
    return getattr(DistanceTreeConstructor(), algo)(distance_matrix)


_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
