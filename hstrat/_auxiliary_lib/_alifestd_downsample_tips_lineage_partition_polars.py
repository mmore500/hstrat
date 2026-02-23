import argparse
import contextlib
import functools
import gc
import logging
import os
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import opytional as opyt
import polars as pl
from tqdm import tqdm

from ._RngStateContext import RngStateContext
from ._add_bool_arg import add_bool_arg
from ._alifestd_calc_mrca_id_vector_asexual_polars import (
    alifestd_calc_mrca_id_vector_asexual_polars,
)
from ._alifestd_downsample_tips_lineage_asexual import (
    _alifestd_downsample_tips_lineage_select_target_id,
)
from ._alifestd_downsample_tips_lineage_partition_asexual import (
    _alifestd_downsample_tips_lineage_partition_impl,
)
from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
)
from ._alifestd_mark_leaves_polars import alifestd_mark_leaves_polars
from ._alifestd_prune_extinct_lineages_polars import (
    alifestd_prune_extinct_lineages_polars,
)
from ._alifestd_topological_sensitivity_warned_polars import (
    alifestd_topological_sensitivity_warned_polars,
)
from ._alifestd_try_add_ancestor_id_col_polars import (
    alifestd_try_add_ancestor_id_col_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


@alifestd_topological_sensitivity_warned_polars(
    insert=False,
    delete=True,
    update=False,
)
def alifestd_downsample_tips_lineage_partition_polars(
    phylogeny_df: pl.DataFrame,
    n_tips: typing.Optional[int] = None,
    seed: typing.Optional[int] = None,
    *,
    criterion_delta: str = "origin_time",
    criterion_partition: str = "origin_time",
    criterion_target: str = "origin_time",
    progress_wrap: typing.Callable = lambda x: x,
) -> pl.DataFrame:
    """Retain one leaf per partition group, chosen by proximity to the
    lineage of a target leaf.

    Selects a target leaf as the leaf with the largest `criterion_target`
    value (ties broken randomly). For each leaf, the most recent common
    ancestor (MRCA) with the target leaf is identified and the "off-lineage
    delta" is computed as the absolute difference between the leaf's
    `criterion_delta` value and its MRCA's `criterion_delta` value.

    Leaves are grouped by their `criterion_partition` value. When
    `n_tips` is an integer, partition values are coarsened by ranking and
    integer-dividing to form exactly `n_tips` groups. When `n_tips` is
    ``None``, each distinct partition value forms its own group. Within
    each group, the single leaf with the smallest off-lineage delta is
    retained.

    Only supports asexual phylogenies.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    n_tips : int, optional
        Desired number of partition groups (and thus retained tips).
        If ``None``, every distinct ``criterion_partition`` value forms
        its own group.
    seed : int, optional
        Random seed for reproducible target-leaf selection when there are
        ties in `criterion_target`.
    criterion_delta : str, default "origin_time"
        Column name used to compute the off-lineage delta for each leaf.
        The delta is the absolute difference between a leaf's value and
        its MRCA's value in this column.
    criterion_partition : str, default "origin_time"
        Column name used to partition leaves into groups.
    criterion_target : str, default "origin_time"
        Column name used to select the target leaf. The leaf with the
        largest value in this column is chosen as the target. Note that
        ties are broken by random sample, allowing a seed to be
        provided.
    progress_wrap : Callable, optional
        Pass tqdm or equivalent to display a progress bar.

    Raises
    ------
    NotImplementedError
        If `phylogeny_df` has no "ancestor_id" column or if ids are
        non-contiguous or not topologically sorted.
    ValueError
        If `criterion_delta`, `criterion_partition`, or
        `criterion_target` is not a column in `phylogeny_df`.

    Returns
    -------
    polars.DataFrame
        The pruned phylogeny in alife standard format.

    See Also
    --------
    alifestd_downsample_tips_lineage_partition_asexual :
        Pandas-based implementation.
    """
    schema_names = phylogeny_df.lazy().collect_schema().names()
    for criterion in (
        criterion_delta,
        criterion_partition,
        criterion_target,
    ):
        if criterion not in schema_names:
            raise ValueError(
                f"criterion column {criterion!r} not found in phylogeny_df",
            )

    if phylogeny_df.lazy().limit(1).collect().is_empty():
        return phylogeny_df

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        "adding ancestor_id col...",
    )
    phylogeny_df = alifestd_try_add_ancestor_id_col_polars(phylogeny_df)
    schema_names = phylogeny_df.lazy().collect_schema().names()
    if "ancestor_id" not in schema_names:
        raise NotImplementedError(
            "alifestd_downsample_tips_lineage_partition_polars only "
            "supports asexual phylogenies.",
        )

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        "checking contiguous ids...",
    )
    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError(
            "non-contiguous ids not yet supported",
        )

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        "checking topological sort...",
    )
    if not alifestd_is_topologically_sorted_polars(phylogeny_df):
        raise NotImplementedError(
            "topologically unsorted rows not yet supported",
        )

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        "marking leaves...",
    )
    phylogeny_df = alifestd_mark_leaves_polars(phylogeny_df)

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        "collecting is_leaf values...",
    )
    is_leaf = (
        phylogeny_df.lazy().select("is_leaf").collect().to_series().to_numpy()
    )

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        "collecting criterion_target values...",
    )
    target_values = (
        phylogeny_df.lazy()
        .select(criterion_target)
        .collect()
        .to_series()
        .to_numpy()
    )

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        "selecting target leaf...",
    )
    with opyt.apply_if_or_else(seed, RngStateContext, contextlib.nullcontext):
        target_id = _alifestd_downsample_tips_lineage_select_target_id(
            is_leaf, target_values
        )

    del target_values
    gc.collect()

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        "collecting criterion_delta values...",
    )
    criterion_values = (
        phylogeny_df.lazy()
        .select(criterion_delta)
        .collect()
        .to_series()
        .to_numpy()
    )

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        "collecting criterion_partition values...",
    )
    partition_values = (
        phylogeny_df.lazy()
        .select(criterion_partition)
        .collect()
        .to_series()
        .to_numpy()
    )

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: "
        f"computing mrca vector for {target_id=}...",
    )
    mrca_vector = alifestd_calc_mrca_id_vector_asexual_polars(
        phylogeny_df, target_id=target_id, progress_wrap=progress_wrap
    )
    is_extant = _alifestd_downsample_tips_lineage_partition_impl(
        is_leaf=is_leaf,
        criterion_values=criterion_values,
        partition_values=partition_values,
        mrca_vector=mrca_vector,
        n_tips=n_tips,
    )

    logging.info(
        "- alifestd_downsample_tips_lineage_partition_polars: pruning...",
    )
    phylogeny_df = phylogeny_df.with_columns(
        extant=is_extant,
    )
    return alifestd_prune_extinct_lineages_polars(phylogeny_df).drop(
        "extant",
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Retain one leaf per partition group, chosen by proximity to the
lineage of a target leaf.

The target leaf is chosen as the leaf with the largest
`--criterion-target` value. For each leaf, the off-lineage delta is
the absolute difference between the leaf's `--criterion-delta` value
and its MRCA's `--criterion-delta` value with respect to the target.
Leaves are grouped by their `--criterion-partition` value. When `-n`
is given, partition values are coarsened into `-n` groups by ranking
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

See Also
========
hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_partition_asexual :
    CLI entrypoint for Pandas-based implementation.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_partition_polars",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "-n",
        default=None,
        type=int,
        help="Number of partition groups (default: one per distinct value).",
    )
    parser.add_argument(
        "--criterion-delta",
        default="origin_time",
        type=str,
        help="Column used to compute off-lineage delta (default: origin_time).",
    )
    parser.add_argument(
        "--criterion-partition",
        default="origin_time",
        type=str,
        help="Column used to partition leaves (default: origin_time).",
    )
    parser.add_argument(
        "--criterion-target",
        default="origin_time",
        type=str,
        help="Column used to select the target leaf (default: origin_time).",
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

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_partition_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=functools.partial(
                    alifestd_downsample_tips_lineage_partition_polars,
                    n_tips=args.n,
                    seed=args.seed,
                    criterion_delta=args.criterion_delta,
                    criterion_partition=args.criterion_partition,
                    criterion_target=args.criterion_target,
                    progress_wrap=tqdm,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
                overridden_arguments="ignore",  # seed is overridden
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
