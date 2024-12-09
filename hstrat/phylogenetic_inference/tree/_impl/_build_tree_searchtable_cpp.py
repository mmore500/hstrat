import typing

from _build_tree_searchtable_cpp_native import build_normal
import numpy as np
import opytional as opyt
import pandas as pd
import tqdm

from ...._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    alifestd_make_empty,
    alifestd_try_add_ancestor_list_col,
    argsort,
)


def _finalize_records(
    records: dict[str, np.ndarray],
    sorted_labels: typing.List[str],
    force_common_ancestry: bool,
) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df["origin_time"] = df["rank"]
    df["taxon_label"] = [str(sorted_labels[i]) for i in df["dstream_data_id"]]

    multiple_true_roots = (
        (df["id"] != 0) & (df["ancestor_id"] == 0)
    ).sum() > 1
    if multiple_true_roots and not force_common_ancestry:
        raise ValueError(
            "Reconstruction resulted in multiple independent trees, "
            "due to artifacts definitively sharing no common ancestor. "
            "Consider setting force_common_ancestry=True.",
        )

    return alifestd_try_add_ancestor_list_col(df, mutate=True)


def build_tree_searchtable_cpp(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    progress_wrap: typing.Callable = lambda x: x,
    force_common_ancestry: bool = False,
) -> pd.DataFrame:
    """
    Uses the consolidated algorithm to build a tree, using a
    searchtable to access elements thereof.
    """

    pop_len = len(population)
    if pop_len == 0:
        return alifestd_make_empty()

    taxon_labels = list(
        opyt.or_value(
            taxon_labels,
            map(int, range(pop_len)),
        )
    )
    sort_order = argsort([x.GetNumStrataDeposited() for x in population])
    sorted_labels = [taxon_labels[i] for i in sort_order]
    sorted_population = [population[i] for i in sort_order]

    records = build_normal(
        [*range(len(sorted_population))],
        [x.GetNumStrataDeposited() for x in sorted_population],
        [[*x.IterRetainedRanks()] for x in sorted_population],
        [[*x.IterRetainedDifferentia()] for x in sorted_population],
        (tqdm.tqdm if progress_wrap is tqdm.tqdm else None),
    )

    return _finalize_records(
        records,
        sorted_labels,
        force_common_ancestry,
    )
