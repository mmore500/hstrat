"""Shared helpers for tests of tree-free pairwise origin-time builders."""

import functools
import os

import numpy as np
import polars as pl

from hstrat.dataframe import surface_test_drive
from hstrat.dataframe._impl._origin_time_cpp_impl_stub import pair_estimate
from hstrat.dataframe._impl._surface_explode_tips import (
    coalesce_dstream_data_id,
    surface_explode_tips,
    tips_cpp_args,
)

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@functools.lru_cache(maxsize=None)
def make_population(
    dstream_algo: str = "dstream.steady_algo",
    dstream_S: int = 64,
    bitwidth: int = 1,
) -> pl.DataFrame:
    """Surface annotations for tips of a reference phylogeny."""
    df = pl.read_csv(f"{assets}/nk_ecoeaselection.csv")
    return surface_test_drive(
        df,
        dstream_algo=dstream_algo,
        dstream_S=dstream_S,
        stratum_differentia_bit_width=bitwidth,
    )


def direct_all_pairs_total(pop: pl.DataFrame) -> float:
    """Sum of pairwise origin-time estimates over all tip pairs."""
    tips = surface_explode_tips(coalesce_dstream_data_id(pop))
    args = tips_cpp_args(tips)
    n = len(tips)
    return sum(
        pair_estimate(*args, a, b) for a in range(n) for b in range(a + 1, n)
    )


def tree_all_pairs_total(phylo: pl.DataFrame) -> float:
    """Sum over nodes of origin time times the number of leaf pairs whose
    most recent common ancestor is the node.

    Ids must be contiguous and topologically sorted (ancestors first).
    """
    ids = phylo["id"].to_numpy().astype(np.int64)
    ancestors = phylo["ancestor_id"].to_numpy().astype(np.int64)
    assert np.array_equal(ids, np.arange(len(ids)))
    assert (ancestors <= ids).all()
    times = phylo["origin_time"].to_numpy()
    num_children = np.bincount(ancestors[ancestors != ids], minlength=len(ids))
    size = (num_children == 0).astype(np.float64)
    sum_sq = np.zeros(len(ids))
    for v in reversed(range(len(ids))):  # descendants first
        if ancestors[v] != v:
            size[ancestors[v]] += size[v]
            sum_sq[ancestors[v]] += size[v] ** 2
    weight = np.where(num_children > 0, (size**2 - sum_sq) / 2, 0.0)
    return float((weight * times).sum())


def is_chronological(phylo: pl.DataFrame) -> bool:
    """Are no inner nodes assigned earlier times than their ancestors?"""
    ids = phylo["id"].to_numpy().astype(np.int64)
    ancestors = phylo["ancestor_id"].to_numpy().astype(np.int64)
    times = phylo["origin_time"].to_numpy()
    num_children = np.bincount(ancestors[ancestors != ids], minlength=len(ids))
    inner = (num_children > 0) & (ancestors != ids)
    inner &= num_children[ancestors] > 0
    return bool(
        (times[inner] >= times[ancestors[inner]] - 1e-9).all(),
    )
