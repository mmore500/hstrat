import argparse
import functools
import gc
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


@alifestd_topological_sensitivity_warned(
    insert=False,
    delete=True,
    update=True,
)
def alifestd_delete_trunk_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
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
    if "is_trunk" not in phylogeny_df:
        raise ValueError(
            "`is_trunk` column not provided, trunk is unspecified"
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    has_contiguous_ids = bool(alifestd_has_contiguous_ids(phylogeny_df))
    logging.info(f"- alifestd_delete_trunk_asexual: {has_contiguous_ids=}")
    if has_contiguous_ids:
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    logging.info(
        "- alifestd_delete_trunk_asexual: marking ancestor_is_trunk...",
    )
    if has_contiguous_ids:
        phylogeny_df["ancestor_is_trunk"] = phylogeny_df[
            "is_trunk"
        ].to_numpy()[phylogeny_df["ancestor_id"]]
    else:
        phylogeny_df["ancestor_is_trunk"] = phylogeny_df.loc[
            phylogeny_df["ancestor_id"], "is_trunk"
        ].to_numpy()

    logging.info("- alifestd_delete_trunk_asexual: testing special cases...")
    if np.any(phylogeny_df["is_trunk"] & ~phylogeny_df["ancestor_is_trunk"]):
        raise ValueError("specified trunk is non-contiguous")

    if phylogeny_df["is_trunk"].sum() == 0:
        return phylogeny_df

    if "ancestor_id" in phylogeny_df:
        logging.info(
            "- alifestd_delete_trunk_asexual: updating ancestor_id...",
        )
        phylogeny_df.loc[
            phylogeny_df["ancestor_is_trunk"], "ancestor_id"
        ] = phylogeny_df.loc[
            phylogeny_df["ancestor_is_trunk"], "id"
        ].to_numpy()

    if "ancestor_list" in phylogeny_df:
        logging.info(
            "- alifestd_delete_trunk_asexual: updating ancestor_list...",
        )
        phylogeny_df.loc[
            phylogeny_df["ancestor_is_trunk"], "ancestor_list"
        ] = "[none]"

    gc.collect()

    logging.info("- alifestd_delete_trunk_asexual: filtering should_keep...")
    should_keep = ~phylogeny_df["is_trunk"]
    res = phylogeny_df.loc[should_keep].reset_index(drop=True)

    assert res["is_trunk"].sum() == 0
    return res


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
        dfcli_module="hstrat._auxiliary_lib._alifestd_delete_trunk_asexual",
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
    logging.info("hstrat version %s", get_hstrat_version())

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_delete_trunk_asexual", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_delete_trunk_asexual,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
