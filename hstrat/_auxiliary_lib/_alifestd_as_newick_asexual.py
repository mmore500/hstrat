from collections import defaultdict
import logging
import typing

import more_itertools as mit
import numpy as np
import opytional as opyt
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_origin_time_delta_asexual import (
    alifestd_mark_origin_time_delta_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_traversal_postorder_asexual import (
    alifestd_unfurl_traversal_postorder_asexual,
)
from ._jit import jit

_UNSAFE_SYMBOLS = (";", "(", ")", ",", "[", "]", ":", "'")


@jit
def _format_newick_repr(taxon_label: str, origin_time_delta: str) -> str:
    # adapted from https://github.com/niemasd/TreeSwift/blob/63b8979fb5e616ba89079d44e594682683c1365e/treeswift/Node.py#L129
    label = taxon_label

    for c in _UNSAFE_SYMBOLS:
        if c in label:
            label = label.join("''")
            break

    if origin_time_delta != "nan":
        if "." in origin_time_delta:
            origin_time_delta = origin_time_delta.rstrip("0").rstrip(".")
        label = f"{label}:{origin_time_delta}"

    return label


def alifestd_as_newick_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    label_key: str = "id",
    progress_wrap=lambda x: x,
) -> str:
    """Convert phylogeny dataframe to Newick format."""

    logging.info(
        "creating newick string for alifestd df "
        f"with shape {phylogeny_df.shape}",
    )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    logging.info("adding ancestor id column, if not present")
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    logging.info("setting up `origin_time_delta` column...")
    if "origin_time_delta" in phylogeny_df.columns:
        logging.info("... already present!")
    elif "origin_time" in phylogeny_df.columns:
        logging.info("... calculating from `origin_time`...")
        phylogeny_df = alifestd_mark_origin_time_delta_asexual(
            phylogeny_df, mutate=True
        )
    else:
        logging.info("... marking null")
        phylogeny_df["origin_time_delta"] = np.nan

    logging.info("calculating postorder traversal order...")
    postorder_ids = alifestd_unfurl_traversal_postorder_asexual(phylogeny_df)

    logging.info("preparing labels...")
    phylogeny_df["__hstrat_label"] = opyt.apply_if_or_value(
        label_key, phylogeny_df.__getitem__, ""
    )
    phylogeny_df["__hstrat_label"] = phylogeny_df["__hstrat_label"].astype(str)

    logging.info("creating newick string...")
    child_newick_reprs = defaultdict(list)
    for id_, taxon_label, origin_time_delta, ancestor_id in progress_wrap(
        phylogeny_df.loc[
            postorder_ids,
            ["id", "__hstrat_label", "origin_time_delta", "ancestor_id"],
        ].astype(
            {"origin_time_delta": str},
        ).to_numpy(),
    ):
        newick_repr = _format_newick_repr(taxon_label, origin_time_delta)

        children_reprs = child_newick_reprs.pop(id_, [])
        if children_reprs:
            newick_repr = f"({','.join(children_reprs)}){newick_repr}"

        child_newick_reprs[ancestor_id].append(newick_repr)

    logging.info(
        f"finalizing newick string for {len(child_newick_reprs)} trees...",
    )
    result = ";\n".join(map(mit.one, child_newick_reprs.values())) + ";"
    logging.info(f"{len(result)=} {result[:20]=}")
    return result
