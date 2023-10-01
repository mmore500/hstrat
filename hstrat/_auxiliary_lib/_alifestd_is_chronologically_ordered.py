import io
import warnings

import pandas as pd

from ._alifestd_find_chronological_inconsistency import (
    alifestd_find_chronological_inconsistency,
)
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids


def _report_diagnosis(df: pd.DataFrame, taxon_id: int) -> None:
    warning_lines = [""]
    append = warning_lines.append

    append(f"chronological inconsitency found!")
    append(f"=================================")
    append(f"in phylogeny with {len(df)} rows")
    buf = io.StringIO()
    df.info(buf=buf, verbose=True)
    append(buf.getvalue())
    append(f"id values range from {df['id'].min()} to {df['id'].max()}")
    append(f"there are {df['id'].isna().sum()} nan id values")
    append(f"there are {df['id'].nunique()} unique id values")
    append(
        f"with {df['id'].is_monotonic_increasing=} "
        f"{df['id'].is_monotonic_decreasing=}",
    )

    ot = df["origin_time"]
    append(f"origin_time values range from {ot.min()} to {ot.max()}")
    append(f"there are {ot.nunique()} unique origin_time values")
    append(f"there are {ot.isna().sum()} nan origin_time values")
    append(
        f"with {ot.is_monotonic_increasing=} {ot.is_monotonic_decreasing=}",
    )

    append("")
    append("")
    append(f"chronological inconsistency occurs at {taxon_id=}")
    (index,) = df[df["id"] == taxon_id].index
    loc = df[df["id"] == taxon_id].index.get_loc(index)
    append(f"for {taxon_id=}, position is {index=} {loc=}")

    origin_time = df.at[index, "origin_time"]
    append(f"for {taxon_id=}, {origin_time=}")
    taxon_origin_time = origin_time

    if "ancestor_id" in df.columns:
        ancestor_id = df.at[index, "ancestor_id"]
        append(f"for {taxon_id=}, {ancestor_id=}")

    ancestor_list = df.at[index, "ancestor_list"]
    ancestor_ids = alifestd_parse_ancestor_ids(ancestor_list)
    append(f"for {taxon_id=}, {ancestor_list=} and {ancestor_ids=}")

    for i, ancestor_id in enumerate(ancestor_ids):
        append("")
        (index,) = df[df["id"] == ancestor_id].index
        loc = df[df["id"] == ancestor_id].index.get_loc(index)
        append(f"for {i}th {ancestor_id=}, position is {index=} {loc=}")

        origin_time = df.at[index, "origin_time"]
        prefix = f"for {i}th {ancestor_id=}, {origin_time=} so "
        ancestor_origin_time = origin_time
        time_delta = taxon_origin_time - ancestor_origin_time
        append(f"{prefix}{time_delta=}")
        if time_delta < 0:
            append(">" * len(prefix) + f" ^^^^^^^^^ time delta is negative!")

    warnings.warn("\n".join(warning_lines))


def alifestd_is_chronologically_ordered(
    phylogeny_df: pd.DataFrame,
    diagnose: bool = True,
) -> bool:
    """Are all organisms listed after members of their `ancestor_list`?

    Input dataframe is not mutated by this operation.
    """

    res = alifestd_find_chronological_inconsistency(phylogeny_df)
    if diagnose and res is not None:
        _report_diagnosis(phylogeny_df, res)
    return res is None
