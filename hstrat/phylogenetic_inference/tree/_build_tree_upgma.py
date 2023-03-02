import typing

import pandas as pd

from ..._auxiliary_lib import BioPhyloTree
from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._impl import build_tree_biopython_distance


def build_tree_upgma(
    population: typing.Sequence[HereditaryStratigraphicColumn],
    estimator: str,
    prior: typing.Union[str, typing.Any],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
    negative_origin_time_correction_method: typing.Optional[str] = None,
) -> pd.DataFrame:

    return build_tree_biopython_distance(
        "upgma",
        population,
        estimator,
        prior,
        taxon_labels,
        force_common_ancestry,
        negative_origin_time_correction_method,
    )
