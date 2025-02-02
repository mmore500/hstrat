import typing
from unittest import mock

import more_itertools as mit
import numpy as np
import opytional as opyt
import pandas as pd
import polars as pl

from ...._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    alifestd_make_empty,
    alifestd_try_add_ancestor_list_col,
    argsort,
)
from ._build_tree_searchtable_cpp_impl_stub import (
    Records,
    build_tree_searchtable_cpp_from_exploded,
    build_tree_searchtable_cpp_from_nested,
    collapse_unifurcations,
    extend_tree_searchtable_cpp_from_exploded,
    extract_records_to_dict,
    placeholder_value,
)


def _finalize_records(
    records: dict[str, np.ndarray],
    sorted_labels: typing.List[str],
    force_common_ancestry: bool,
) -> pd.DataFrame:
    """Collate as phylogeny dataframe in alife standard format."""
    df = pd.DataFrame(
        {k: v for k, v in records.items() if not k.startswith("search_")},
    )
    df["origin_time"] = df["rank"]
    df["taxon_label"] = [
        str(sorted_labels[i]) if i != placeholder_value else "_inner_node"
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


def _explode_population(
    sorted_population: typing.Sequence[HereditaryStratigraphicArtifact],
) -> pl.DataFrame:
    """Create DataFrame with one row for each retained stratum across all
    population members."""
    return pl.DataFrame(
        {
            "data_ids": [
                i
                for i, ann in enumerate(sorted_population)
                for __ in range(ann.GetNumStrataRetained())
            ],
            "num_strata_depositeds": [
                ann.GetNumStrataDeposited()
                for ann in sorted_population
                for __ in range(ann.GetNumStrataRetained())
            ],
            "ranks": [
                rank
                for ann in sorted_population
                for rank in ann.IterRetainedRanks()
            ],
            "differentiae": [
                differentia
                for ann in sorted_population
                for differentia in ann.IterRetainedDifferentia()
            ],
        },
        schema={
            "data_ids": pl.UInt64,
            "num_strata_depositeds": pl.UInt64,
            "ranks": pl.UInt64,
            "differentiae": pl.UInt64,
        },
    )


def build_tree_searchtable_cpp(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    progress_wrap: typing.Optional[typing.Callable] = None,
    force_common_ancestry: bool = False,
    _entry_point: typing.Literal[
        "batched_small",
        "batched_medium",
        "batched_large",
        "batched_small_nocollapse",
        "batched_medium_nocollapse",
        "batched_large_nocollapse",
        "nested",
        "exploded",
    ] = "nested",
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
    _entry_point : Literal, default "nested"
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
        res = alifestd_make_empty()
        res["origin_time"] = pd.Series(dtype=int)
        res["taxon_label"] = None
        return res

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
        exploded_df = _explode_population(sorted_population)
        records = build_tree_searchtable_cpp_from_exploded(
            exploded_df["data_ids"].to_numpy(),
            exploded_df["num_strata_depositeds"].to_numpy(),
            exploded_df["ranks"].to_numpy(),
            exploded_df["differentiae"].to_numpy(),
            opyt.or_value(progress_wrap, mock.Mock()),
        )
    elif _entry_point.startswith("batched_"):
        exploded_df = _explode_population(sorted_population)
        batch_size = {
            "batched_small": 10,
            "batched_medium": 1_000,
            "batched_large": 10_000_000,
            "batched_small_nocollapse": 10,
            "batched_medium_nocollapse": 1_000,
            "batched_large_nocollapse": 10_000_000,
        }[_entry_point]
        records = Records(len(exploded_df) * 4)
        for partition_dfs in mit.sliced(
            exploded_df.partition_by("data_ids"), batch_size
        ):
            slice_df = pl.concat(partition_dfs)
            extend_tree_searchtable_cpp_from_exploded(
                records,
                slice_df["data_ids"].to_numpy(),
                slice_df["num_strata_depositeds"].to_numpy(),
                slice_df["ranks"].to_numpy(),
                slice_df["differentiae"].to_numpy(),
                opyt.or_value(progress_wrap, mock.Mock()),
            )
            if not _entry_point.endswith("_nocollapse"):
                records = collapse_unifurcations(records, dropped_only=True)
        records = extract_records_to_dict(records)
    else:
        raise ValueError(f"Invalid entry point: {_entry_point}")

    assert len(records["dstream_data_id"]) >= len(sorted_population) + 1
    return _finalize_records(
        records,
        sorted_labels,
        force_common_ancestry,
    )
