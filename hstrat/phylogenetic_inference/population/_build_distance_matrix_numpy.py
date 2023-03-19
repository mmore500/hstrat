import itertools as it
import typing

import numpy as np

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ..pairwise import estimate_patristic_distance_between


def build_distance_matrix_numpy(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    estimator: str,
    prior: typing.Union[str, typing.Any],
    force_common_ancestry: typing.Optional[bool] = False,
) -> np.ndarray:
    """Compute all-pairs patristic distance among a population of extant
    hereditary stratigraphic columns.

    Parameters
    ----------
    population : Sequence[HereditaryStratigraphicArtifact]
        The extant hereditary stratigraphic columns to compare.

        The ordering of rows and columns within the returned matrix will
        correspond to the ordering of columns in this sequence.
    estimator : {"maximum_likelihood", "unbiased"}
        What patristic distance estimation method should be used? Options are
        "maximum_likelihood" or "unbiased".

        See `estimate_ranks_since_mrca_with` for discussion of estimator
        options.
    prior :
        Prior probability density distribution over possible generations of the
        MRCA for MRCA estimation.

        See `estimate_ranks_since_mrca_with` for discussion of prior
        options.
    force_common_ancestry : Optional[bool], optional
        How should columns that definively share no common ancestry be handled?

        If set to True, treat columns with no common ancestry as if they
        shared a common ancestor immediately before the genesis of the
        lineages. If set to False, set the patristic distance between columns
        with no common ancestry as NaN.

        If set to None, as default, the presence of columns that definitively
        share no common ancestry will raise a ValueError.

    Returns
    -------
    np.ndarray
        The patristic distance matrix of the population, a square numpy array
        of shape (len(population), len(population)).

    Raises
    ------
    ValueError
        If the distance between two columns that definitively share no common
        ancestry are attempted to be computed without setting
        `force_common_ancestry`.
    """

    matrix = np.empty((len(population), len(population)))

    pairings = it.combinations_with_replacement(range(len(population)), 2)

    for a, b in pairings:
        patristic_distance = estimate_patristic_distance_between(
            population[a],
            population[b],
            estimator,
            prior,
        )

        if patristic_distance is None and force_common_ancestry is None:
            raise ValueError(
                f"Definitive independent origins detected for {a} and {b};"
                "Set force_common_ancestry to handle this case."
            )
        elif patristic_distance is None and force_common_ancestry:
            max_patristic_distance = (
                population[a].GetNumStrataDeposited()
                + population[b].GetNumStrataDeposited()
            )
            matrix[a][b] = max_patristic_distance
            matrix[b][a] = max_patristic_distance
        elif patristic_distance is None and not force_common_ancestry:
            matrix[a][b] = np.nan
            matrix[b][a] = np.nan
        elif a == b:
            # this is important to do manually:
            # estimators are not guaranteed to yield zero or near zero
            # patristic distance for identical columns
            matrix[a][b] = 0.0
            matrix[b][a] = 0.0
        else:
            matrix[a][b] = patristic_distance
            matrix[b][a] = patristic_distance

    return matrix
