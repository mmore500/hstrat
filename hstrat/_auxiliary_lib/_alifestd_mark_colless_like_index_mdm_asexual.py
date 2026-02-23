import argparse
import logging
import math
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_num_children_asexual import (
    alifestd_mark_num_children_asexual,
)
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._log_context_duration import log_context_duration


@jit(nopython=True)
def _colless_like_fast_path(
    ancestor_ids: np.ndarray,
    diss_type: int,
) -> np.ndarray:
    """Implementation detail for Colless-like index functions.

    Parameters
    ----------
    ancestor_ids : np.ndarray
        Array of ancestor IDs (contiguous, topologically sorted).
    diss_type : int
        Dissimilarity type: 0=MDM, 1=variance, 2=std dev.
    """
    n = len(ancestor_ids)

    # Compute out-degree (number of children) for each node
    num_children = np.zeros(n, dtype=np.int64)
    for tup in enumerate(ancestor_ids):
        # workaround: unpack inside loop body to avoid numba
        # generator-in-zip KeyError bug with `for a, b in generator`
        idx, ancestor_id = tup
        if ancestor_id != idx:  # Not a root
            num_children[ancestor_id] += 1

    # Compute f-size bottom-up
    # f(k) = ln(k + e), so f(0) = ln(e) = 1.0
    # delta_f(T_v) = f(deg(v)) + sum of delta_f(T_c) for children c
    f_size = np.zeros(n, dtype=np.float64)
    for tup in enumerate(num_children):
        # workaround: unpack inside loop body to avoid numba
        # generator-in-zip KeyError bug with `for a, b in generator`
        idx, k = tup
        f_size[idx] = math.log(k + math.e)

    # Accumulate f-size bottom-up (add children's f-sizes to parent)
    for idx in range(n - 1, -1, -1):  # reversed enumerate
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:  # Not a root
            f_size[ancestor_id] += f_size[idx]

    # Build CSR-like structure of children f-sizes per parent
    offsets = np.zeros(n + 1, dtype=np.int64)
    for tup in enumerate(num_children):
        # workaround: unpack inside loop body to avoid numba
        # generator-in-zip KeyError bug with `for a, b in generator`
        i, k = tup
        offsets[i + 1] = offsets[i] + k

    total_children = offsets[n]
    children_fsize = np.zeros(total_children, dtype=np.float64)
    fill_pos = np.zeros(n, dtype=np.int64)
    for tup in enumerate(ancestor_ids):
        # workaround: unpack inside loop body to avoid numba
        # generator-in-zip KeyError bug with `for a, b in generator`
        idx, ancestor_id = tup
        if ancestor_id != idx:  # Not a root
            pos = offsets[ancestor_id] + fill_pos[ancestor_id]
            children_fsize[pos] = f_size[idx]
            fill_pos[ancestor_id] += 1

    # Compute local balance using selected dissimilarity
    local_balance = np.zeros(n, dtype=np.float64)
    for tup in enumerate(num_children):
        # workaround: unpack inside loop body to avoid numba
        # generator-in-zip KeyError bug with `for a, b in generator`
        idx, k = tup
        if k >= 2:
            start = offsets[idx]
            end = offsets[idx + 1]

            vals = children_fsize[start:end]

            if diss_type == 0:  # MDM
                median = np.median(vals)
                # MDM = (1/k) * sum |x_i - median|
                local_balance[idx] = np.sum(np.abs(vals - median)) / k

            elif diss_type == 1:  # Variance (ddof=1)
                # np.var uses ddof=0; apply Bessel correction
                local_balance[idx] = np.var(vals) * k / (k - 1)

            elif diss_type == 2:  # Standard deviation (ddof=1)
                local_balance[idx] = math.sqrt(np.var(vals) * k / (k - 1))

    # Accumulate subtree Colless-like index bottom-up
    colless_like = np.zeros(n, dtype=np.float64)
    for idx in range(n - 1, -1, -1):  # reversed enumerate
        ancestor_id = ancestor_ids[idx]
        colless_like[idx] += local_balance[idx]
        if ancestor_id != idx:  # Not a root
            colless_like[ancestor_id] += colless_like[idx]

    return colless_like


def _colless_like_slow_path(
    phylogeny_df: pd.DataFrame,
    diss_type: str,
) -> np.ndarray:
    """Implementation detail for Colless-like index functions."""
    phylogeny_df.index = phylogeny_df["id"]

    # Build children mapping
    children_of = {id_: [] for id_ in phylogeny_df.index}
    for node_id in phylogeny_df.index:
        ancestor_id = phylogeny_df.at[node_id, "ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            children_of[ancestor_id].append(node_id)

    # Compute f-size bottom-up
    f_size = {}
    for node_id in reversed(phylogeny_df.index):
        k = phylogeny_df.at[node_id, "num_children"]
        f_size[node_id] = math.log(k + math.e) + sum(
            f_size[c] for c in children_of[node_id]
        )

    # Compute local balance using selected dissimilarity
    local_balance = {}
    for node_id in phylogeny_df.index:
        k = phylogeny_df.at[node_id, "num_children"]
        if k >= 2:
            vals = np.array(
                [f_size[c] for c in children_of[node_id]],
            )

            if diss_type == "mdm":
                med = np.median(vals)
                local_balance[node_id] = np.sum(np.abs(vals - med)) / k
            elif diss_type == "var":
                local_balance[node_id] = np.var(vals, ddof=1)
            elif diss_type == "sd":
                local_balance[node_id] = np.std(vals, ddof=1)
            else:
                assert False
        else:
            local_balance[node_id] = 0.0

    # Accumulate bottom-up
    for node_id in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[node_id, "ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            local_balance[ancestor_id] += local_balance[node_id]

    return phylogeny_df["id"].map(local_balance).values


def _alifestd_mark_colless_like_index_asexual_impl(
    phylogeny_df: pd.DataFrame,
    col_name: str,
    diss_type: str,
    mutate: bool = False,
) -> pd.DataFrame:
    """Common implementation for Colless-like index variants.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Alife standard DataFrame.
    col_name : str
        Name of the output column.
    diss_type : str
        Dissimilarity type: "mdm", "var", or "sd".
    mutate : bool, optional
        If True, modify the input DataFrame in place.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if phylogeny_df.empty:
        phylogeny_df[col_name] = pd.Series(dtype=float)
        return phylogeny_df

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df[col_name] = _colless_like_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            ["mdm", "var", "sd"].index(diss_type),
        )
    else:
        if "num_children" not in phylogeny_df.columns:
            phylogeny_df = alifestd_mark_num_children_asexual(
                phylogeny_df,
                mutate=True,
            )
        phylogeny_df[col_name] = _colless_like_slow_path(
            phylogeny_df,
            diss_type,
        )

    return phylogeny_df


def alifestd_mark_colless_like_index_mdm_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `colless_like_index_mdm` with Colless-like index
    using mean deviation from the median (MDM) as dissimilarity.

    Computes the Colless-like balance index from Mir, Rossello, and
    Rotger (2018) that supports polytomies. Uses weight function
    f(k) = ln(k + e) and MDM dissimilarity.

    For each internal node v with children v_1, ..., v_k:
        bal(v) = MDM(delta_f(T_v1), ..., delta_f(T_vk))

    where delta_f(T) is the f-size of subtree T, defined as the sum
    of f(deg(u)) over all nodes u in T, and

        MDM(x_1, ..., x_k) = (1/k) * sum |x_i - median(x)|

    The Colless-like index at a node is the sum of balance values
    across all internal nodes in its subtree.

    Leaf nodes will have Colless-like index 0. The root node contains
    the Colless-like index for the entire tree.

    A topological sort will be applied if `phylogeny_df` is not
    topologically sorted. Dataframe reindexing (e.g., df.index) may
    be applied.

    Input dataframe is not mutated by this operation unless `mutate`
    set True. If mutate set True, operation does not occur in place;
    still use return value to get transformed phylogeny dataframe.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Alife standard DataFrame containing the phylogenetic
        relationships.

    mutate : bool, optional
        If True, modify the input DataFrame in place. Default is
        False.

    Returns
    -------
    pd.DataFrame
        Phylogeny DataFrame with an additional column
        "colless_like_index_mdm" containing the Colless-like
        imbalance index for the subtree rooted at each node.

    References
    ----------
    Mir, A., Rossello, F., & Rotger, L. (2018). Sound Colless-like
    balance indices for multifurcating trees. PLOS ONE, 13(9),
    e0203401. https://doi.org/10.1371/journal.pone.0203401

    See Also
    --------
    alifestd_mark_colless_like_index_var_asexual :
        Colless-like index using variance dissimilarity.
    alifestd_mark_colless_like_index_sd_asexual :
        Colless-like index using standard deviation dissimilarity.
    alifestd_mark_colless_index_asexual :
        Classic Colless index for strictly bifurcating trees.
    """
    return _alifestd_mark_colless_like_index_asexual_impl(
        phylogeny_df,
        "colless_like_index_mdm",
        "mdm",
        mutate=mutate,
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add column `colless_like_index_mdm` with Colless-like index using mean deviation from the median (MDM) as dissimilarity.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_colless_like_index_mdm_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_colless_like_index_mdm_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_colless_like_index_mdm_asexual,
            ),
        )
