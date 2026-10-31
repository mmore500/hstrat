import numpy as np
from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat.dataframe.build_trie_upgma import surface_build_tree

from .._origin_time_testing import (
    direct_all_pairs_total,
    is_chronological,
    make_population,
    tree_all_pairs_total,
)


@pytest.mark.parametrize(
    "dstream_algo", ["dstream.steady_algo", "dstream.tilted_algo"]
)
@pytest.mark.parametrize("bitwidth", [1, 8])
def test_all_pairs_total_exact(dstream_algo: str, bitwidth: int):
    pop = make_population(dstream_algo, 64, bitwidth)
    phylo = surface_build_tree(pop)
    expected = direct_all_pairs_total(pop)
    assert tree_all_pairs_total(phylo) == pytest.approx(expected, rel=1e-9)


def test_tree_shape():
    pop = make_population()
    phylo = surface_build_tree(pop)
    assert len(pop) < len(phylo) <= 2 * len(pop) - 1
    assert pfl.alifestd_is_topologically_sorted_polars(phylo)
    assert pfl.alifestd_has_contiguous_ids_polars(phylo)
    ids, ancestors = phylo["id"].to_numpy(), phylo["ancestor_id"].to_numpy()
    num_children = np.bincount(ancestors[ancestors != ids], minlength=len(ids))
    assert (num_children[num_children > 0] >= 2).all()
    assert (ancestors == ids).sum() == 1
    assert is_chronological(phylo)


def test_leaves():
    pop = make_population()
    phylo = surface_build_tree(pop)
    leaves = phylo.filter(pl.col("dstream_data_id").is_not_null())
    assert len(leaves) == len(pop)
    assert sorted(leaves["td_source_id"]) == sorted(pop["td_source_id"])
    # leaf origin time is dstream_T - 1 - dstream_S, i.e., one less than
    # number of strata deposited since founding
    expected = leaves.join(
        pop.select("td_source_id", pl.col("origin_time").alias("td_time")),
        on="td_source_id",
    )
    assert (expected["origin_time"] == expected["td_time"] - 1).all()
    inner = phylo.filter(pl.col("dstream_data_id").is_null())
    assert inner["td_source_id"].is_null().all()


def test_trie_postprocessor_applied():
    pop = make_population()

    def postprocessor(trie, p_differentia_collision, mutate, progress_wrap):
        assert isinstance(trie, pl.DataFrame)
        assert p_differentia_collision == 0.5
        assert "origin_time" in trie.columns
        return trie.with_columns(foo=pl.lit("bar"))

    phylo = surface_build_tree(pop, trie_postprocessor=postprocessor)
    assert (phylo["foo"] == "bar").all()


def test_empty():
    pop = make_population().head(0)
    phylo = surface_build_tree(pop)
    assert phylo.is_empty()
    assert {"id", "ancestor_id", "origin_time", "dstream_data_id"} <= {
        *phylo.columns
    }


def test_single():
    pop = make_population().head(1)
    phylo = surface_build_tree(pop)
    assert len(phylo) == 1
    assert phylo["ancestor_id"].item() == phylo["id"].item()


@pytest.mark.parametrize("num_samples", [1, 64])
@pytest.mark.parametrize("direct_max", [1, 64])
def test_sampling_parameters(num_samples: int, direct_max: int):
    pop = make_population("dstream.tilted_algo", 64, 1)
    phylo = surface_build_tree(
        pop, num_samples=num_samples, direct_max=direct_max, seed=2
    )
    expected = direct_all_pairs_total(pop)
    assert tree_all_pairs_total(phylo) == pytest.approx(expected, rel=1e-9)
    assert is_chronological(phylo)
