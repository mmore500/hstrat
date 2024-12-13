import typing
from unittest import mock

import numpy as np
import opytional as opyt
import pandas as pd

from ...._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    alifestd_make_empty,
    alifestd_try_add_ancestor_list_col,
    argsort,
)
from ._build_tree_searchtable_cpp_impl_stub import (
    build_tree_searchtable_cpp_from_exploded,
    build_tree_searchtable_cpp_from_nested,
)


def _finalize_records(
    records: dict[str, np.ndarray],
    sorted_labels: typing.List[str],
    force_common_ancestry: bool,
) -> pd.DataFrame:
    """Collate as phylogeny dataframe in alife standard format."""
    df = pd.DataFrame(records)
    df["origin_time"] = df["rank"]
    df["taxon_label"] = [
        str(sorted_labels[i]) if i != (2**31 - 1) else "_inner_node"
        for i in df["dstream_data_id"]
    ]

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
    progress_wrap: typing.Optional[typing.Callable] = None,
    force_common_ancestry: bool = False,
    _entry_point: typing.Literal["nested", "exploded"] = "nested",
) -> pd.DataFrame:
    """C++-based implementation of `build_tree_searchtable`.

    Parameters
    ----------
    population: Sequence[HereditaryStratigraphicArtifact]
        Hereditary stratigraphic columns corresponding to extant population members.

        Each member of population will correspond to a unique leaf node in the
        reconstructed tree.
    taxon_labels: Optional[Iterable], optional
        How should leaf nodes representing extant hereditary stratigraphic
        columns be named?

        Label order should correspond to the order of corresponding hereditary
        stratigraphic columns within `population`. If None, taxons will be
        named according to their numerical index.
    force_common_ancestry: bool, default False
        How should columns that definitively share no common ancestry be
        handled?

        If set to True, treat columns with no common ancestry as if they
        shared a common ancestor immediately before the genesis of the
        lineages. If set to False, columns within `population` that
        definitively do not share common ancestry will raise a ValueError.
    progress_wrap : Callable, optional
        Pass tqdm or equivalent to display a progress bar.
    _entry_point : Literal["nested", "exploded"], default "nested"
        Which implementation interface should be called?

        For internal use in testing.

    Returns
    -------
    pd.DataFrame
        The reconstructed phylogenetic tree in alife standard format.

    Notes
    -----
    See `build_tree_searchtable` for algorithm overview.
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

    if _entry_point == "nested":
        records = build_tree_searchtable_cpp_from_nested(
            [*range(len(sorted_population))],
            [ann.GetNumStrataDeposited() for ann in sorted_population],
            [[*ann.IterRetainedRanks()] for ann in sorted_population],
            [[*ann.IterRetainedDifferentia()] for ann in sorted_population],
            opyt.or_value(progress_wrap, mock.Mock()),
        )
    elif _entry_point == "exploded":
        records = build_tree_searchtable_cpp_from_exploded(
            [
                i
                for i, ann in enumerate(sorted_population)
                for __ in range(ann.GetNumStrataRetained())
            ],
            [
                ann.GetNumStrataDeposited()
                for ann in sorted_population
                for __ in range(ann.GetNumStrataRetained())
            ],
            [
                rank
                for ann in sorted_population
                for rank in ann.IterRetainedRanks()
            ],
            [
                differentia
                for ann in sorted_population
                for differentia in ann.IterRetainedDifferentia()
            ],
            opyt.or_value(progress_wrap, mock.Mock()),
        )
    else:
        raise ValueError(f"Invalid entry point: {_entry_point}")

    return _finalize_records(
        records,
        sorted_labels,
        force_common_ancestry,
    )
