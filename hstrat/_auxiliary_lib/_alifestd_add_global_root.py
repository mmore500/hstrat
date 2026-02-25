import argparse
import functools
import logging
import os
import types
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_find_root_ids import alifestd_find_root_ids
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._eval_kwargs import eval_kwargs
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


@alifestd_topological_sensitivity_warned(
    insert=True,
    delete=False,
    update=True,
)
def alifestd_add_global_root(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    root_attrs: typing.Mapping[str, typing.Any] = types.MappingProxyType({}),
) -> pd.DataFrame:
    """Add a new global root node that all existing roots point to.

    The new root node will have columns `id`, `ancestor_id` (if applicable),
    `ancestor_list` (if applicable), and any columns specified in
    `root_attrs`. All other columns will be NaN for the new root row.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Phylogeny dataframe in alife standard format.
    mutate : bool, default False
        If True, allows mutation of the input dataframe.
    root_attrs : Mapping[str, Any], default {}
        Column values to set on the new global root row, e.g.,
        ``{"origin_time": 0.0, "taxon_label": "root"}``.

        Keys ``"id"``, ``"ancestor_id"``, and ``"ancestor_list"`` are
        reserved and may not be specified; a `ValueError` is raised if
        any are present.

    Returns
    -------
    pd.DataFrame
        The phylogeny dataframe with a new global root added.

    Raises
    ------
    ValueError
        If `root_attrs` contains reserved keys.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    bad_keys = {"id", "ancestor_id", "ancestor_list"} & root_attrs.keys()
    if bad_keys:
        raise ValueError(
            f"root_attrs must not contain reserved keys {bad_keys}; "
            "these are set automatically"
        )

    # Create new root id
    new_root_id = phylogeny_df["id"].max() + 1 if not phylogeny_df.empty else 0

    # Build the new root row
    new_root = {
        "id": new_root_id,
        **(
            {"ancestor_id": new_root_id}
            if "ancestor_id" in phylogeny_df
            else {}
        ),
        **(
            {"ancestor_list": "[none]"}
            if "ancestor_list" in phylogeny_df
            else {}
        ),
        **root_attrs,
    }

    # Point existing roots to the new global root
    root_ids = alifestd_find_root_ids(phylogeny_df)
    root_mask = phylogeny_df["id"].isin(root_ids)

    if "ancestor_id" in phylogeny_df:
        phylogeny_df.loc[root_mask, "ancestor_id"] = new_root_id

    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[root_mask, "ancestor_list"] = f"[{new_root_id}]"

    # Append the new root row (vertical concat; mismatched columns get NaN)
    new_root_df = pd.DataFrame([new_root])
    res = pd.concat([phylogeny_df, new_root_df], axis=0, ignore_index=True)

    return res


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add a global root node that all existing roots point to.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_add_global_root",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "--root-attr",
        action="append",
        dest="root_attrs",
        type=str,
        default=[],
        help=(
            "Column value to set on the new root row. "
            "Provide as 'key=value'. "
            "Specify multiple attrs by using this flag multiple times. "
            "Arguments will be evaluated as Python expressions. "
            "Example: --root-attr 'origin_time=0.0'"
        ),
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
        "hstrat._auxiliary_lib._alifestd_add_global_root",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_add_global_root,
                    root_attrs=eval_kwargs(args.root_attrs),
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
