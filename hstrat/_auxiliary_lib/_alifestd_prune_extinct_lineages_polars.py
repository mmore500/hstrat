import argparse
import functools
import gc
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._add_bool_arg import add_bool_arg
from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
)
from ._alifestd_prune_extinct_lineages_asexual import (
    _create_has_extant_descendant_contiguous_sorted,
)
from ._alifestd_topological_sensitivity_warned_polars import (
    alifestd_topological_sensitivity_warned_polars,
)
from ._begin_prod_logging import begin_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration
from ._log_memory_usage import log_memory_usage


@alifestd_topological_sensitivity_warned_polars(
    insert=False,
    delete=True,
    update=False,
)
def alifestd_prune_extinct_lineages_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Drop taxa without extant descendants.

    An "extant" column, if provided, is used to determine extant taxa.
    Otherwise, taxa with inf or nan "destruction_time" are considered extant.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.

    Raises
    ------
    NotImplementedError
        If `phylogeny_df` has no "ancestor_id" column.
    NotImplementedError
        If `phylogeny_df` has non-contiguous ids.
    NotImplementedError
        If `phylogeny_df` is not topologically sorted.
    ValueError
        If `phylogeny_df` has neither "extant" nor "destruction_time" columns.

    Returns
    -------
    polars.DataFrame
        The pruned phylogeny in alife standard format.

    See Also
    --------
    alifestd_prune_extinct_lineages_asexual :
        Pandas-based implementation.
    """
    logging.info(
        "- alifestd_prune_extinct_lineages_polars: collecting schema...",
    )
    schema_names = phylogeny_df.lazy().collect_schema().names()
    if "ancestor_id" not in schema_names:
        raise NotImplementedError("ancestor_id column required")
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_prune_extinct_lineages_polars: checking empty...",
    )
    if phylogeny_df.lazy().limit(1).collect().is_empty():
        return phylogeny_df
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_prune_extinct_lineages_polars: "
        "checking contiguous ids...",
    )
    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError("non-contiguous ids not yet supported")
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_prune_extinct_lineages_polars: "
        "checking topological sort...",
    )
    if not alifestd_is_topologically_sorted_polars(phylogeny_df):
        raise NotImplementedError(
            "polars topological sort not yet implemented",
        )
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_prune_extinct_lineages_polars: "
        "determining extant mask...",
    )
    if "extant" in schema_names:
        extant_mask = phylogeny_df.lazy().select("extant")
    elif "destruction_time" in schema_names:
        extant_mask = phylogeny_df.lazy().select(
            ~pl.col("destruction_time").is_finite()
        )
    else:
        raise ValueError('Need "extant" or "destruction_time" column.')
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_prune_extinct_lineages_polars: "
        "collecting extant mask...",
    )
    extant_mask = extant_mask.cast(pl.Boolean).collect().to_series().to_numpy()
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_prune_extinct_lineages_polars: "
        "collecting ancestor_ids...",
    )
    ancestor_ids = (
        phylogeny_df.lazy()
        .select("ancestor_id")
        .cast(pl.UInt64)
        .collect()
        .to_series()
        .to_numpy()
    )
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_prune_extinct_lineages_polars: "
        "calculating has_extant_descendant...",
    )
    has_extant_descendant = _create_has_extant_descendant_contiguous_sorted(
        ancestor_ids.copy(),  # must copy to remove read-only flag...
        extant_mask.copy(),  # ... for numba compatibility
    )
    del ancestor_ids, extant_mask
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_prune_extinct_lineages_polars: marking...",
    )
    phylogeny_df = phylogeny_df.with_columns(
        alifestd_has_extant_descendant=has_extant_descendant,
    )
    del has_extant_descendant
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_prune_extinct_lineages_polars: filtering...",
    )
    return phylogeny_df.filter(
        pl.col("alifestd_has_extant_descendant"),
    ).drop("alifestd_has_extant_descendant")


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Drop taxa without extant descendants.

An "extant" column, if provided, is used to determine extant taxa.
Otherwise, taxa with inf or nan "destruction_time" are considered extant.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.
Otherwise, no action is taken.

- Requires 'extant' or 'destruction_time' column.

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual :
    CLI entrypoint for Pandas-based implementation.
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_polars",
        dfcli_version=get_hstrat_version(),
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
    begin_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=functools.partial(
                    alifestd_prune_extinct_lineages_polars,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
