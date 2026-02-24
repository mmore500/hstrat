import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._add_bool_arg import add_bool_arg
from ._alifestd_topological_sensitivity_warned_polars import (
    alifestd_topological_sensitivity_warned_polars,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


@alifestd_topological_sensitivity_warned_polars(
    insert=False,
    delete=True,
    update=True,
)
def alifestd_delete_trunk_asexual_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Delete entries masked by `is_trunk` column.

    Masked entries must be contiguous, meaning that no non-trunk entry can
    be an ancestor of a trunk entry. Children of deleted entries will become
    roots.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_collapse_trunk_asexual
    """
    phylogeny_df = phylogeny_df.lazy().collect()  # lazy not yet implemented

    if "is_trunk" not in phylogeny_df:
        raise ValueError(
            "`is_trunk` column not provided, trunk is unspecified",
        )

    if "ancestor_list" in phylogeny_df:
        raise NotImplementedError

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    has_contiguous_ids = phylogeny_df.select(
        pl.col("id").diff() == 1
    ).to_series().all() and (phylogeny_df["id"].first() == 0)
    if not has_contiguous_ids:
        raise NotImplementedError("non-contiguous ids not yet supported")

    logging.info(
        "- alifestd_delete_trunk_asexual_polars: marking ancestor_is_trunk...",
    )
    phylogeny_df = phylogeny_df.with_columns(
        ancestor_is_trunk=pl.col("is_trunk").gather(
            pl.col("ancestor_id"),
        )
    )

    logging.info(
        "- alifestd_delete_trunk_asexual_polars: testing special cases..."
    )
    if (phylogeny_df["is_trunk"] & ~phylogeny_df["ancestor_is_trunk"]).any():
        raise ValueError("specified trunk is non-contiguous")

    if phylogeny_df["is_trunk"].sum() == 0:
        return phylogeny_df

    logging.info(
        "- alifestd_delete_trunk_asexual_polars: updating ancestor_id...",
    )
    phylogeny_df = phylogeny_df.with_columns(
        ancestor_id=pl.when(pl.col("ancestor_is_trunk"))
        .then(pl.col("id"))
        .otherwise(pl.col("ancestor_id")),
    )

    logging.info("- alifestd_delete_trunk_asexual_polars: filtering...")
    phylogeny_df = phylogeny_df.filter(~pl.col("is_trunk"))

    assert phylogeny_df["is_trunk"].sum() == 0
    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Delete entries masked by `is_trunk` column.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_delete_trunk_asexual_polars",
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
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_delete_trunk_asexual_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=lambda df: alifestd_delete_trunk_asexual_polars(
                    df,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
