import argparse
import contextlib
import functools
import logging
import os
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import opytional as opyt
import pandas as pd
from tqdm import tqdm

from ._RngStateContext import RngStateContext
from ._add_bool_arg import add_bool_arg
from ._alifestd_calc_mrca_id_vector_asexual import (
    alifestd_calc_mrca_id_vector_asexual,
)
from ._alifestd_downsample_tips_lineage_asexual import (
    _alifestd_downsample_tips_lineage_select_target_id,
)
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_prune_extinct_lineages_asexual import (
    alifestd_prune_extinct_lineages_asexual,
)
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def _alifestd_downsample_tips_lineage_stratified_impl(
    is_leaf: np.ndarray,
    criterion_values: np.ndarray,
    stratify_values: np.ndarray,
    mrca_vector: np.ndarray,
    n_tips: typing.Optional[int] = None,
    n_tips_per_stratum: int = 1,
) -> np.ndarray:
    """Shared numpy implementation for stratified lineage tip
    downsampling.

    Computes off-lineage deltas from a pre-computed MRCA vector and
    returns a boolean extant mask, selecting up to
    ``n_tips_per_stratum`` leaves with the smallest delta per
    stratified group.

    When `n_tips` is an integer, stratified values are coarsened by
    ranking and integer-dividing so that exactly
    ``n_tips // n_tips_per_stratum`` groups are formed.  When `n_tips`
    is ``None``, each distinct stratified value defines its own group.

    Parameters
    ----------
    is_leaf : numpy.ndarray
        Boolean array indicating which taxa are leaves.
    criterion_values : numpy.ndarray
        Values used to compute off-lineage delta (all taxa).
    stratify_values : numpy.ndarray
        Values used to stratify leaves into groups (all taxa).
    mrca_vector : numpy.ndarray
        Integer array of MRCA ids for each taxon with respect to the
        target leaf.  Taxa in a different tree should have ``-1``.
    n_tips : int, optional
        Desired number of retained tips.  If ``None``, every distinct
        stratified value forms its own group and
        ``n_tips_per_stratum`` tips are kept per group.
    n_tips_per_stratum : int, default 1
        Number of tips to retain per stratified group.

    Returns
    -------
    numpy.ndarray
        Boolean array of length ``len(is_leaf)`` marking retained taxa.
    """
    # Taxa with no common ancestor (different tree) get -1 from MRCA
    # calc; replace with a safe dummy id (0) so the lookup doesn't fail,
    # then exclude these taxa from selection below.
    no_mrca_mask = mrca_vector == -1
    safe_mrca = np.where(no_mrca_mask, 0, mrca_vector)

    logging.info(
        "_alifestd_downsample_tips_lineage_stratified_impl: "
        "calculating off lineage delta...",
    )
    off_lineage_delta = np.abs(
        criterion_values - criterion_values[safe_mrca],
    )

    # Select eligible leaves
    logging.info(
        "_alifestd_downsample_tips_lineage_stratified_impl: "
        "filtering leaf eligibility...",
    )
    is_eligible = is_leaf & ~no_mrca_mask
    eligible_ids = np.flatnonzero(is_eligible)
    eligible_deltas = off_lineage_delta[is_eligible]
    eligible_stratified = stratify_values[is_eligible]

    # Coarsen stratified values if n_tips is specified
    if n_tips is not None:
        logging.info(
            "_alifestd_downsample_tips_lineage_stratified_impl: "
            "coarsening stratified values...",
        )
        n_groups = n_tips // n_tips_per_stratum
        unique_sorted = np.unique(eligible_stratified)
        n_unique = len(unique_sorted)
        ranks = np.searchsorted(unique_sorted, eligible_stratified)
        eligible_stratified = ranks * n_groups // n_unique
        assert len(np.unique(eligible_stratified)) == min(n_groups, n_unique)

    # Per-stratum selection: for each group, keep up to
    # n_tips_per_stratum leaves with the smallest delta.
    logging.info(
        "_alifestd_downsample_tips_lineage_stratified_impl: "
        "selecting kept ids per stratum...",
    )
    # Vectorized: sort by (stratum, delta), then pick the first
    # n_tips_per_stratum occurrences of each stratum.
    sort_order = np.lexsort((eligible_deltas, eligible_stratified))
    sorted_strata = eligible_stratified[sort_order]
    sorted_ids = eligible_ids[sort_order]

    stratum_change = np.diff(sorted_strata, prepend=np.nan) != 0
    stratum_starts = np.flatnonzero(stratum_change)
    stratum_lengths = np.diff(
        np.append(stratum_starts, len(sorted_strata)),
    )
    start_for_each = np.repeat(stratum_starts, stratum_lengths)
    position_in_stratum = np.arange(len(sorted_strata)) - start_for_each
    keep_mask = position_in_stratum < n_tips_per_stratum
    kept_ids = sorted_ids[keep_mask]

    logging.info(
        "_alifestd_downsample_tips_lineage_stratified_impl: "
        "building extant mask...",
    )
    return np.bincount(kept_ids, minlength=len(is_leaf)).astype(bool)


@alifestd_topological_sensitivity_warned(
    insert=False,
    delete=True,
    update=False,
)
def alifestd_downsample_tips_lineage_stratified_asexual(
    phylogeny_df: pd.DataFrame,
    n_tips: typing.Optional[int] = None,
    mutate: bool = False,
    seed: typing.Optional[int] = None,
    *,
    criterion_delta: str = "origin_time",
    criterion_stratify: str = "origin_time",
    criterion_target: str = "origin_time",
    n_tips_per_stratum: int = 1,
    progress_wrap: typing.Callable = lambda x: x,
) -> pd.DataFrame:
    """Retain leaves per stratified group, chosen by proximity to the
    lineage of a target leaf.

    Selects a target leaf as the leaf with the largest `criterion_target`
    value (ties broken randomly). For each non-target leaf, the most
    recent common ancestor (MRCA) of that leaf and the target leaf is
    identified, and the "off-lineage delta" is computed as the absolute
    difference between that leaf's `criterion_delta` value and the
    MRCA's `criterion_delta` value.

    Leaves are grouped by their `criterion_stratify` value. When
    `n_tips` is an integer, stratified values are coarsened by ranking
    and integer-dividing to form exactly ``n_tips // n_tips_per_stratum``
    groups. When `n_tips` is ``None``, each distinct stratified value
    forms its own group (without ranking). Within each group, the
    ``n_tips_per_stratum`` leaves with the smallest off-lineage delta
    are retained.

    Only supports asexual phylogenies.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    n_tips : int, optional
        Desired number of retained tips.  If ``None``, every distinct
        ``criterion_stratify`` value forms its own group.
    mutate : bool, default False
        Are side effects on the input argument `phylogeny_df` allowed?
    seed : int, optional
        Random seed for reproducible target-leaf selection when there are
        ties in `criterion_target`.
    criterion_delta : str, default "origin_time"
        Column name used to compute the off-lineage delta for each leaf.
        The delta is the absolute difference between a leaf's value and
        its MRCA's value in this column.
    criterion_stratify : str, default "origin_time"
        Column name used to stratify leaves into groups.
    criterion_target : str, default "origin_time"
        Column name used to select the target leaf. The leaf with the
        largest value in this column is chosen as the target. Note that
        ties are broken by random sample, allowing a seed to be
        provided.
    n_tips_per_stratum : int, default 1
        Number of tips to retain per stratified group.  Must evenly
        divide ``n_tips`` when ``n_tips`` is not ``None``.
    progress_wrap : Callable, optional
        Pass tqdm or equivalent to display a progress bar.

    Raises
    ------
    ValueError
        If `criterion_delta`, `criterion_stratify`, or
        `criterion_target` is not a column in `phylogeny_df`.
    ValueError
        If ``n_tips`` is not ``None`` and ``n_tips_per_stratum`` does
        not evenly divide ``n_tips``.

    Returns
    -------
    pandas.DataFrame
        The pruned phylogeny in alife standard format.
    """
    if n_tips is not None and n_tips % n_tips_per_stratum != 0:
        raise ValueError(
            f"n_tips_per_stratum={n_tips_per_stratum} does not evenly "
            f"divide n_tips={n_tips}",
        )

    for criterion in (
        criterion_delta,
        criterion_stratify,
        criterion_target,
    ):
        if criterion not in phylogeny_df.columns:
            raise ValueError(
                f"criterion column {criterion!r} not found in phylogeny_df",
            )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if phylogeny_df.empty:
        return phylogeny_df

    logging.info(
        "- alifestd_downsample_tips_lineage_stratified_asexual: "
        "adding ancestor_id col...",
    )
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_downsample_tips_lineage_stratified_asexual only "
            "supports asexual phylogenies.",
        )

    logging.info(
        "- alifestd_downsample_tips_lineage_stratified_asexual: "
        "marking leaves...",
    )
    if "is_leaf" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_leaves(phylogeny_df)

    logging.info(
        "- alifestd_downsample_tips_lineage_stratified_asexual: "
        "checking contiguous ids...",
    )
    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        # non-contiguous id branch not tested because
        # alifestd_calc_mrca_id_vector_asexual doesn't support it
        raise NotImplementedError(
            "non-contiguous ids not yet supported",
        )

    is_leaf = phylogeny_df["is_leaf"].to_numpy()
    target_values = phylogeny_df[criterion_target].to_numpy()
    criterion_values = phylogeny_df[criterion_delta].to_numpy()
    stratify_values = phylogeny_df[criterion_stratify].to_numpy()

    with opyt.apply_if_or_else(seed, RngStateContext, contextlib.nullcontext):
        target_id = _alifestd_downsample_tips_lineage_select_target_id(
            is_leaf, target_values
        )

    logging.info(
        "- alifestd_downsample_tips_lineage_stratified_asexual: "
        "computing mrca vector...",
    )
    mrca_vector = alifestd_calc_mrca_id_vector_asexual(
        phylogeny_df, target_id=target_id, progress_wrap=progress_wrap
    )

    logging.info(
        "- alifestd_downsample_tips_lineage_stratified_asexual: "
        "computing lineage stratified downsample...",
    )
    is_extant = _alifestd_downsample_tips_lineage_stratified_impl(
        is_leaf=is_leaf,
        criterion_values=criterion_values,
        stratify_values=stratify_values,
        mrca_vector=mrca_vector,
        n_tips=n_tips,
        n_tips_per_stratum=n_tips_per_stratum,
    )

    logging.info(
        "- alifestd_downsample_tips_lineage_stratified_asexual: pruning...",
    )
    phylogeny_df["extant"] = is_extant
    return alifestd_prune_extinct_lineages_asexual(
        phylogeny_df, mutate=True
    ).drop(columns=["extant"])


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Retain one leaf per stratified group, chosen by proximity to the
lineage of a target leaf.

The target leaf is chosen as the leaf with the largest
`--criterion-target` value. For each leaf, the off-lineage delta is
the absolute difference between that leaf's `--criterion-delta` value
and the MRCA's `--criterion-delta` value (where the MRCA is of that
leaf and the target).
Leaves are grouped by their `--criterion-stratify` value. When `-n`
is given, stratified values are coarsened into `-n` groups by ranking
and integer division. Within each group, the leaf with the smallest
delta is retained.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.
Otherwise, no action is taken.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_stratified_asexual",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "-n",
        default=None,
        type=int,
        help="Number of stratified groups (default: one per distinct value).",
    )
    parser.add_argument(
        "--criterion-delta",
        default="origin_time",
        type=str,
        help="Column used to compute off-lineage delta (default: origin_time).",
    )
    parser.add_argument(
        "--criterion-stratify",
        default="origin_time",
        type=str,
        help="Column used to stratify leaves (default: origin_time).",
    )
    parser.add_argument(
        "--criterion-target",
        default="origin_time",
        type=str,
        help="Column used to select the target leaf (default: origin_time).",
    )
    parser.add_argument(
        "--n-tips-per-stratum",
        default=1,
        type=int,
        help="Number of tips per stratum (default: 1).",
    )
    parser.add_argument(
        "--seed",
        default=None,
        dest="seed",
        help="Integer seed for deterministic target-leaf selection.",
        type=int,
    )
    add_bool_arg(
        parser,
        "ignore-topological-sensitivity",
        default=False,
        help="suppress topological sensitivity warning (default: False)",
    )
    add_bool_arg(
        parser,
        "drop-topological-sensitivity",
        default=False,
        help="drop topology-sensitive columns from output (default: False)",
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()
    logging.info("hstrat version %s", get_hstrat_version())

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_stratified_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_downsample_tips_lineage_stratified_asexual,
                    n_tips=args.n,
                    seed=args.seed,
                    criterion_delta=args.criterion_delta,
                    criterion_stratify=args.criterion_stratify,
                    criterion_target=args.criterion_target,
                    n_tips_per_stratum=args.n_tips_per_stratum,
                    progress_wrap=tqdm,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
            overridden_arguments="ignore",  # seed is overridden
        )
