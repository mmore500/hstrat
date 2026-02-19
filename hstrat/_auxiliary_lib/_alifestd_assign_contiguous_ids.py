import argparse
import logging
import os
import typing

from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import joinem
import numpy as np
import pandas as pd

from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._jit_numba_dict_t import jit_numba_dict_t
from ._jit_numpy_int64_t import jit_numpy_int64_t
from ._log_context_duration import log_context_duration


@jit(nopython=True)
def _reassign_ids_asexual(
    ids: np.ndarray,
    ancestor_ids: np.ndarray,
) -> np.ndarray:
    max_id = np.max(ids)

    if max_id > len(ids) * 5:
        reassignment = jit_numba_dict_t.empty(
            key_type=jit_numpy_int64_t,
            value_type=jit_numpy_int64_t,
        )
        for id_ in ids:
            reassignment[id_] = len(reassignment)
        return np.array(
            [reassignment[ancestor_id] for ancestor_id in ancestor_ids]
        )
    else:
        reassignment = np.empty(max_id + 1, dtype=np.int64)
        for i, id_ in enumerate(ids):
            reassignment[id_] = i
        return np.array(
            [reassignment[ancestor_id] for ancestor_id in ancestor_ids]
        )


@jit(nopython=True)
def _reassign_ids_sexual(ids: np.ndarray) -> typing.Dict[int, int]:
    reassignment = jit_numba_dict_t.empty(
        key_type=jit_numpy_int64_t,
        value_type=jit_numpy_int64_t,
    )
    for id_ in ids:
        reassignment[id_] = len(reassignment)

    return reassignment


def alifestd_assign_contiguous_ids(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Reassign so each organism's id corresponds to its row number.

    Organisms retain the same row location; only id numbers change. Input
    dataframe is not mutated by this operation unless `mutate` True.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    original_ids = phylogeny_df["id"].to_numpy(dtype=np.int64).copy()
    phylogeny_df["id"] = np.arange(len(phylogeny_df))

    if "ancestor_id" in phylogeny_df.columns:
        phylogeny_df["ancestor_id"] = _reassign_ids_asexual(
            original_ids, phylogeny_df["ancestor_id"].to_numpy(dtype=np.int64)
        )
        if "ancestor_list" in phylogeny_df:
            phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
                phylogeny_df["id"], phylogeny_df["ancestor_id"]
            )
    else:
        reassignment = _reassign_ids_sexual(original_ids)
        phylogeny_df["ancestor_list"] = phylogeny_df["ancestor_list"].map(
            lambda ancestor_list_str: str(
                [
                    int(reassignment[ancestor_id])
                    for ancestor_id in alifestd_parse_ancestor_ids(
                        ancestor_list_str
                    )
                ]
            )
        )
        phylogeny_df.loc[
            phylogeny_df["ancestor_list"] == "[]", "ancestor_list"
        ] = "[none]"

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Reassign so each organism's id corresponds to its row number.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_assign_contiguous_ids",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_assign_contiguous_ids", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_assign_contiguous_ids,
            ),
        )
