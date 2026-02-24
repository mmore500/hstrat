import argparse
import functools
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_lineage_asexual import alifestd_unfurl_lineage_asexual
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration
from ._pairwise import pairwise


@alifestd_topological_sensitivity_warned(
    insert=False,
    delete=False,
    update=True,
)
def alifestd_reroot_at_id_asexual(
    phylogeny_df: pd.DataFrame,
    new_root_id: int,
    mutate: bool = False,
) -> pd.DataFrame:
    """Reroot phylogeny, preserving topology.

    Reverses the descendant-to-ancestor relationships of all ancestors of the
    new root. Does not update branch_lengths or edge_lengths columns if
    present.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    new_root_id : int
        The ID of the node to use as the new root of the phylogeny.
    mutate : bool, default False
        Are side effects on the input argument `phylogeny_df` allowed?

    Returns
    -------
    pandas.DataFrame
        The rerooted phylogeny in alife standard format.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    unfurled_lineage = alifestd_unfurl_lineage_asexual(
        phylogeny_df, new_root_id
    )

    # contiguous id implementation
    if alifestd_has_contiguous_ids(phylogeny_df):
        copy_to_slice = unfurled_lineage[1:]
        copy_from_slice = unfurled_lineage[:-1]
        phylogeny_df["ancestor_id"].to_numpy()[copy_to_slice] = phylogeny_df[
            "id"
        ].to_numpy()[copy_from_slice]

        phylogeny_df["ancestor_id"].to_numpy()[new_root_id] = phylogeny_df[
            "id"
        ].to_numpy()[new_root_id]

    # noncontiguous id implementation
    else:
        iloc_lookup = dict(
            zip(phylogeny_df["id"], np.arange(len(phylogeny_df)))
        )
        for ancestor_id, descendant_id in pairwise(reversed(unfurled_lineage)):
            iloc = iloc_lookup[ancestor_id]
            phylogeny_df["ancestor_id"].to_numpy()[iloc] = descendant_id

        new_root_iloc = iloc_lookup[new_root_id]
        phylogeny_df["ancestor_id"].to_numpy()[new_root_iloc] = phylogeny_df[
            "id"
        ].to_numpy()[new_root_iloc]

    # update ancestor list
    phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
        phylogeny_df["id"],
        phylogeny_df["ancestor_id"],
    )
    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Reroot phylogeny at specified node id, preserving topology.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_reroot_at_id_asexual",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "--new-root-id",
        type=int,
        required=True,
        help="id of the node to reroot at",
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
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_reroot_at_id_asexual", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_reroot_at_id_asexual,
                    new_root_id=args.new_root_id,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
