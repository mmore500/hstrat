import argparse
import functools
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_add_inner_knuckles_asexual import (
    alifestd_add_inner_knuckles_asexual,
)
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_mark_node_depth_asexual import alifestd_mark_node_depth_asexual
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._begin_prod_logging import begin_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


@alifestd_topological_sensitivity_warned(
    insert=True,
    delete=False,
    update=True,
)
def alifestd_add_inner_niblings_asexual(
    phylogeny_df: pd.DataFrame, mutate: bool = False
) -> pd.DataFrame:
    """For all inner nodes, add a subtending unifurcation, adding a "nibling"
    leaf as the child of the knuckle.

    Here, "nibling" refers to a leaf that is a neice/nephew of the inner node.
    If not topologically sorted, a topological sort will be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_add_inner_knuckles_asexual(
        phylogeny_df, mutate=True
    )

    phylogeny_df = alifestd_mark_node_depth_asexual(phylogeny_df, mutate=True)

    phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    nibling_mask = (phylogeny_df["node_depth"] & 1).astype(bool) & (
        ~phylogeny_df["is_leaf"]
    )

    nibling_df = phylogeny_df[nibling_mask].copy()

    id_delta = phylogeny_df["id"].max() + 1
    nibling_df["id"] += id_delta
    nibling_df["is_leaf"] = True

    if nibling_df["id"].min() <= phylogeny_df["id"].max():
        print(nibling_df["id"].min(), phylogeny_df["id"].max())
        raise ValueError("overflow in new id assigment")

    return pd.concat([phylogeny_df, nibling_df], ignore_index=True)


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

For all inner nodes, add a subtending unifurcation, adding a nibling leaf as the child of the knuckle.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_add_inner_niblings_asexual",
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
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_add_inner_niblings_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_add_inner_niblings_asexual,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
