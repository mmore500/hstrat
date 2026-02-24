import argparse
from collections import Counter
import functools
import logging
import os
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_assign_contiguous_ids import alifestd_assign_contiguous_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._jit_numpy_uint8_t import jit_numpy_uint8_t
from ._log_context_duration import log_context_duration


@jit(nopython=True)
def _collapse_unifurcations(
    ancestor_ids: np.ndarray,
) -> typing.Tuple[np.ndarray, np.ndarray]:
    # assumes contiguous ids

    ref_counts = np.zeros(len(ancestor_ids), dtype=jit_numpy_uint8_t)
    for ancestor_id in ancestor_ids:
        # cap to prevent overflow
        ref_counts[ancestor_id] = min(ref_counts[ancestor_id] + 1, 2)

    ids = np.arange(len(ancestor_ids))

    for pos, ancestor_id in enumerate(ancestor_ids):
        id_ = ids[pos]
        assert id_ == pos
        assert ancestor_id <= id_

        if ref_counts[ancestor_id] == 1:  # root ok
            # percolate ancestor over self
            ancestor_ids[pos] = ancestor_ids[ancestor_id]

    keep_filter = (ref_counts != 1) | (ancestor_ids == ids)

    return keep_filter, ancestor_ids


def _alifestd_collapse_unifurcations_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool,
    root_ancestor_token: str,
) -> pd.DataFrame:
    """Optimized implementation for asexual phylogenies."""

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    original_ids = phylogeny_df["id"].to_numpy().copy()
    if not alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df = alifestd_assign_contiguous_ids(
            phylogeny_df, mutate=True
        )

    logging.info("- alifestd_collapse_unifurcations: calculating reindex...")
    assert (phylogeny_df["id"] >= phylogeny_df["ancestor_id"]).all()
    keep_filter, ancestor_ids = _collapse_unifurcations(
        phylogeny_df["ancestor_id"].to_numpy(),
    )

    logging.info("- alifestd_collapse_unifurcations: applying reindex...")
    phylogeny_df = phylogeny_df.loc[keep_filter].copy()
    phylogeny_df["id"] = original_ids[keep_filter]
    phylogeny_df["ancestor_id"] = original_ids[ancestor_ids[keep_filter]]
    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[:, "ancestor_list"] = alifestd_make_ancestor_list_col(
            phylogeny_df["id"],
            phylogeny_df["ancestor_id"],
            root_ancestor_token=root_ancestor_token,
        )

    return phylogeny_df


@alifestd_topological_sensitivity_warned(
    insert=False,
    delete=True,
    update=True,
)
def alifestd_collapse_unifurcations(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    root_ancestor_token: str = "none",
) -> pd.DataFrame:
    """Pare record to bypass organisms with one ancestor and one descendant.

    May leave a root unifurcation present. See
    `alifestd_delete_unifurcating_roots_asexual`.

    The option `root_ancestor_token` will be sandwiched in brackets to create
    the ancestor list entry for genesis organisms. For example, the token
    "None" will yield the entry "[None]" and the token "" will yield the entry
    "[]". Default "none".

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_collapse_unifurcations_polars :
        Polars-based implementation.
    """
    # special optimized handling for asexual phylogenies
    if alifestd_is_asexual(phylogeny_df):
        return _alifestd_collapse_unifurcations_asexual(
            phylogeny_df,
            mutate=mutate,
            root_ancestor_token=root_ancestor_token,
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    phylogeny_df.set_index("id", drop=False, inplace=True)

    ref_counts = Counter(
        id_
        for ancestor_list_str in phylogeny_df["ancestor_list"]
        for id_ in alifestd_parse_ancestor_ids(ancestor_list_str)
    )

    for id_ in phylogeny_df["id"]:
        ancestor_ids = alifestd_parse_ancestor_ids(
            phylogeny_df.at[id_, "ancestor_list"]
        )
        if len(ancestor_ids) == 1 and ref_counts[id_] == 1:
            # percolate ancestor over self
            (ancestor_id,) = ancestor_ids
            phylogeny_df.loc[id_] = phylogeny_df.loc[ancestor_id]
        elif len(ancestor_ids):
            # update referenced ancestor
            phylogeny_df.at[id_, "ancestor_list"] = str(
                [
                    int(phylogeny_df.at[ancestor_id, "id"])
                    for ancestor_id in ancestor_ids
                ]
            )
        else:
            assert not ancestor_ids
            phylogeny_df.at[id_, "ancestor_list"] = f"[{root_ancestor_token}]"

    assert "ancestor_id" not in phylogeny_df

    return phylogeny_df.drop_duplicates().reset_index(drop=True)


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Pare record to bypass organisms with one ancestor and one descendant.

Data is assumed to be in alife standard format.

Additional Notes
================
- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_collapse_unifurcations_polars :
    Entrypoint for high-performance Polars-based implementation.
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
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
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_collapse_unifurcations,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
