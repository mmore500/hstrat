"""Functions to reconstruct a phylogenetic tree from extant hereditary strata."""

__all__ = []

from itertools import combinations
from numbers import Number
from string import ascii_lowercase
from typing import Any, Iterable

from ..._auxiliary_lib import launder_impl_modules as _launder
from ..._auxiliary_lib import to_tril

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from warnings import warn

import Bio.Phylo.TreeConstruction as BioPhyloTree
import numpy as np

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ..pairwise import (
    calc_rank_of_earliest_detectable_mrca_between,
    calc_ranks_since_mrca_bounds_with,
    does_definitively_have_no_common_ancestor,
)


def distance_matrix_helper(
    x: HereditaryStratigraphicColumn, y: HereditaryStratigraphicColumn
) -> Number:
    mrca_bounds = calc_ranks_since_mrca_bounds_with(x, y, prior="arbitrary")
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
            f"Independent origins detected for {x} and {y}; returning a "
            "distance of 0. Future software versions may raise an error for "
            "this case."
        )
        return 0


def calculate_distance_matrix(
    population: Iterable[HereditaryStratigraphicColumn],
    names: Iterable[Any] = None,
) -> BioPhyloTree.DistanceMatrix:
    matrix_data = np.zeros((len(population), len(population)))

    pairwise = combinations(range(len(population)), 2)

    for a, b in pairwise:
        matrix_data[a][b] = distance_matrix_helper(
            population[a], population[b]
        )

    return BioPhyloTree.DistanceMatrix(
        names=names if names else [str(x) for x in range(len(population))],
        matrix=to_tril(matrix_data.T),
    )


# TODO: turn into a shim function. add a boolean parameter for 'dendropy tree'
def reconstruct_tree(
    distance_matrix: BioPhyloTree.DistanceMatrix,
    algo: Literal["nj", "upgma"] = "upgma",
):
    if algo not in ("nj", "upgma"):
        raise ValueError(
            f"Unsupported reconstruction algorithm {algo}. "
            "Please choose one of 'nj', 'upgma'."
        )
    if not distance_matrix:
        return BioPhyloTree.BaseTree.Tree()
    return getattr(BioPhyloTree.DistanceTreeConstructor(), algo)(
        distance_matrix
    )


_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
