import argparse
import itertools as it
import logging
import os
import typing
import warnings

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd
import sortedcontainers as sc

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_has_multiple_roots import alifestd_has_multiple_roots
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_ot_mrca_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
) -> pd.DataFrame:
    """Appends columns characterizing the Most Recent Common Ancestor (MRCA) of the
    entire extant population at each taxon's `origin_time`.

    The extant population is defined in terms of active lineages: any branch of the
    tree existing at an `origin_time` which contains at least one descendant at or
    after that time.

    New Columns:
    ------------
    ot_mrca_id : int
        The unique identifier of the MRCA for the population that was extant at
        this organism's `origin_time`.

    ot_mrca_time_of : int or float
        The `origin_time` of that MRCA.

    ot_mrca_time_since : int or float
        The duration elapsed between the MRCA's `origin_time` and this taxon's
        `origin_time`.

    A chronological sort will be applied if `phylogeny_df` is not
    chronologically sorted. Dataframe reindexing (e.g., df.index) may be
    applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    # setup
    if alifestd_has_multiple_roots(phylogeny_df):
        raise NotImplementedError()

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)
    phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    contig = alifestd_has_contiguous_ids(phylogeny_df)
    if contig:
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        warnings.warn("mark_ot_mrca_asexual may be slow with uncontiguous ids")
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["ot_mrca_id"] = phylogeny_df["id"].max() + 1
    phylogeny_df["ot_mrca_time_of"] = phylogeny_df["origin_time"].max()
    phylogeny_df["ot_mrca_time_since"] = phylogeny_df["origin_time"].max()

    df = phylogeny_df
    df["bwd_origin_time"] = -df["origin_time"]

    # do calculation
    running_mrca_id = max(
        df["id"],
        default=None,
        key=lambda i: (df.at[i, "origin_time"], df.index.get_loc(i)),
    )  # initial value

    # for optimization
    ot_mrca_ids = []
    ot_mrca_times_of = []
    ot_mrca_times_since = []
    indices = []
    key = df.index.get_loc if not contig else None
    for bwd_origin_time, group in progress_wrap(df.groupby("bwd_origin_time")):
        earliest_id = (
            group["id"].min() if contig else min(group["id"], key=key)
        )

        leaf_mask = group["is_leaf"]
        lineages = sc.SortedSet(
            (*group.loc[leaf_mask, "id"], earliest_id, running_mrca_id),
            key=key,
        )
        while len(lineages) > 1:
            oldest = lineages.pop(-1)
            replacement = df.at[oldest, "ancestor_id"]
            assert replacement != oldest
            lineages.add(replacement)

        (mrca_id,) = lineages
        running_mrca_id = mrca_id

        # set column values
        mrca_time = df.at[mrca_id, "origin_time"]

        size = len(group)
        indices.extend(group["id"])
        ot_mrca_ids.extend(it.repeat(mrca_id, size))
        ot_mrca_times_of.extend(it.repeat(mrca_time, size))
        ot_mrca_times_since.extend(
            it.repeat(-bwd_origin_time - mrca_time, size),
        )

    df.loc[indices, "ot_mrca_id"] = ot_mrca_ids
    df.loc[indices, "ot_mrca_time_of"] = ot_mrca_times_of
    df.loc[indices, "ot_mrca_time_since"] = ot_mrca_times_since
    df.drop("bwd_origin_time", axis=1, inplace=True)
    return df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Append columns characterizing the Most Recent Common Ancestor (MRCA) of the entire extant population at each taxon's `origin_time`.

Data is assumed to be in alife standard format.

Additional Notes
================
- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        allow_abbrev=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_ot_mrca_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()
    logging.info("hstrat version %s", get_hstrat_version())

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_ot_mrca_asexual", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_ot_mrca_asexual,
            ),
        )
