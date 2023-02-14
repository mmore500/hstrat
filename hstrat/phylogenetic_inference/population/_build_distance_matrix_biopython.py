import typing

import Bio.Phylo.TreeConstruction as BioPhyloTree
import opytional as opyt

from ..._auxiliary_lib import to_tril
from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._build_distance_matrix_numpy import build_distance_matrix_numpy


def build_distance_matrix_biopython(
    population: typing.Sequence[HereditaryStratigraphicColumn],
    estimator: str,
    prior: typing.Union[str, typing.Any],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: typing.Optional[bool] = False,
) -> BioPhyloTree.DistanceMatrix:
    """Compute all-pairs patristic distance among a population of extant
    hereditary stratigraphic columns as a BioPython `DistanceMatrix`.

    Parameters
    ----------
    population : Sequence[HereditaryStratigraphicColumn]
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
    taxon_labels : Iterable[str]], optional
        How should leaf nodes representing extant hereditary stratigraphic
        columns be named?

        Label order should correspond to the order of corresponding hereditary
        stratigraphic columns within `population`. If None, taxons will be
        named according to their numerical index.
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

    distance_matrix = build_distance_matrix_numpy(
        population,
        estimator,
        prior,
        force_common_ancestry,
    )
    return BioPhyloTree.DistanceMatrix(
        names=opyt.or_value(
            taxon_labels,
            [*map(str, range(len(population)))],
        ),
        matrix=to_tril(distance_matrix),
    )