import argparse
import functools
import itertools as it
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._jit_numba_dict_t import jit_numba_dict_t
from ._jit_numpy_int64_t import jit_numpy_int64_t
from ._log_context_duration import log_context_duration


@jit(nopython=True)
def _alifestd_splay_polytomies_fast_path(
    ancestor_ids: np.ndarray,
) -> pd.DataFrame:
    """Implementation detail for alifestd_splay_polytomies."""
    i64 = jit_numpy_int64_t
    splay_to_lookup = jit_numba_dict_t.empty(key_type=i64, value_type=i64)
    splay_from_lookup = jit_numba_dict_t.empty(key_type=i64, value_type=i64)

    new_rows = jit_numba_dict_t.empty(key_type=i64, value_type=i64)
    new_row_sources = jit_numba_dict_t.empty(key_type=i64, value_type=i64)
    for id_, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id == id_:  # root
            continue

        if ancestor_id not in splay_to_lookup:
            splayed_from_id = ancestor_id
            splayed_to_id = ancestor_id
        else:
            splayed_from_id = splay_to_lookup[ancestor_id]
            splayed_to_id = len(ancestor_ids) + len(new_rows)

            ancestor_ids[id_] = splayed_to_id
            new_rows[splayed_to_id] = splayed_from_id
            new_row_sources[splayed_to_id] = ancestor_id

        splay_from_lookup[splayed_to_id] = splayed_from_id
        splay_to_lookup[ancestor_id] = splayed_to_id

    # drop unnecessary splays
    dropped_splay_remap = jit_numba_dict_t.empty(key_type=i64, value_type=i64)
    for ancestor_id, splayed_to_id in splay_to_lookup.items():
        if ancestor_id != splayed_to_id:
            splayed_from_id = splay_from_lookup[splayed_to_id]
            assert new_rows[splayed_to_id] == splayed_from_id
            dropped_splay_remap[splayed_to_id] = splayed_from_id
            del new_rows[splayed_to_id]
            del new_row_sources[splayed_to_id]

    # correct dropped splays
    for idx, ancestor_id in enumerate(ancestor_ids):
        splayed_to_id = dropped_splay_remap.get(ancestor_id, ancestor_id)
        ancestor_ids[idx] = splayed_to_id

    new_ids = np.array([*new_rows.keys()], dtype=np.int64)
    new_ancestor_ids = np.array([*new_rows.values()], dtype=np.int64)
    new_source_ids = np.array(
        [new_row_sources[new_id] for new_id in new_ids], dtype=np.int64
    )
    return ancestor_ids, new_source_ids, new_ids, new_ancestor_ids


def _alifestd_splay_polytomies_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for alifestd_splay_polytomies."""
    splay_to_lookup = dict()
    splay_from_lookup = dict()
    phylogeny_df.set_index("id", drop=False, inplace=True)

    new_id_generator = it.count(phylogeny_df["id"].max() + 1)

    new_rows = dict()
    for id_, row in phylogeny_df.iterrows():
        ancestor_id = row["ancestor_id"]
        if ancestor_id == id_:  # root
            continue

        if ancestor_id not in splay_to_lookup:
            splayed_from_id = ancestor_id
            splayed_to_id = ancestor_id
        else:
            splayed_from_id = splay_to_lookup[ancestor_id]
            splayed_to_id = next(new_id_generator)

            phylogeny_df.at[id_, "ancestor_id"] = splayed_to_id
            new_row = phylogeny_df.loc[ancestor_id].copy()
            new_row["id"] = splayed_to_id
            new_row["ancestor_id"] = splayed_from_id
            new_rows[splayed_to_id] = new_row

        splay_from_lookup[splayed_to_id] = splayed_from_id
        splay_to_lookup[ancestor_id] = splayed_to_id

    # drop unnecessary splays
    dropped_splay_remap = dict()
    for ancestor_id, splayed_to_id in splay_to_lookup.items():
        if ancestor_id != splayed_to_id:
            splayed_from_id = splay_from_lookup[splayed_to_id]
            assert new_rows[splayed_to_id]["ancestor_id"] == splayed_from_id
            dropped_splay_remap[splayed_to_id] = splayed_from_id
            del new_rows[splayed_to_id]

    # correct dropped splays
    phylogeny_df["ancestor_id"] = (
        phylogeny_df["ancestor_id"]
        .map(
            {
                **{
                    ancestor_id: ancestor_id
                    for ancestor_id in phylogeny_df["ancestor_id"]
                },
                **dropped_splay_remap,
            }
        )
        .astype(int)
    )

    appendum_df = pd.DataFrame(new_rows.values())
    phylogeny_df = pd.concat([phylogeny_df, appendum_df], ignore_index=True)

    return phylogeny_df.reset_index(drop=True)


@alifestd_topological_sensitivity_warned(
    insert=True,
    delete=False,
    update=True,
)
def alifestd_splay_polytomies(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    r"""Use a simple splay strategy to resolve polytomies, converting them into
    bifurcations.

    For example,
    ```
      1
     /|\
    2 3 4
    ```
    becomes
    ```
      1
     / \
    2   5
       / \
      3   4
    ```

    No adjustments to any branch length columns in `phylogeny_df` are
    performed. However, `origin_time` (as well as all other columns) of a
    polytomy's parent node are duplicated in splayed-out nodes that resolve
    that polytomy. So, nodes added to perform the splaying-out will have zero-
    length subtending branches in this regard (i.e., their origin time will
    match their parent's).

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_asexual(phylogeny_df):
        raise NotImplementedError

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
        (
            phylogeny_df["ancestor_id"],
            new_source_ids,
            new_ids,
            new_ancestor_ids,
        ) = _alifestd_splay_polytomies_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(dtype=np.int64)
        )
        addendum = phylogeny_df.loc[new_source_ids].copy()
        addendum["id"] = new_ids
        addendum["ancestor_id"] = new_ancestor_ids
        phylogeny_df = pd.concat([phylogeny_df, addendum], ignore_index=True)
    else:
        phylogeny_df = _alifestd_splay_polytomies_slow_path(phylogeny_df)

    if "ancestor_list" in phylogeny_df:
        phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
            phylogeny_df["id"], phylogeny_df["ancestor_id"]
        )

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Use a simple splay strategy to resolve polytomies, converting them into bifurcations.

Data is assumed to be in alife standard format.

Additional Notes
================
- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_splay_polytomies",
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
        "hstrat._auxiliary_lib._alifestd_splay_polytomies", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_splay_polytomies,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
