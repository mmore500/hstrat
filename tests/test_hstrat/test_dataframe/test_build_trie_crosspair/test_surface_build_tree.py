from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat.dataframe.build_trie_crosspair import surface_build_tree

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
@pytest.mark.parametrize("pool_inversions", [True, False])
def test_all_pairs_total_exact(
    dstream_algo: str, bitwidth: int, pool_inversions: bool
):
    pop = make_population(dstream_algo, 64, bitwidth)
    phylo = surface_build_tree(pop, pool_inversions=pool_inversions)
    expected = direct_all_pairs_total(pop)
    assert tree_all_pairs_total(phylo) == pytest.approx(expected, rel=1e-9)
    if pool_inversions:
        assert is_chronological(phylo)


def test_tree_shape():
    pop = make_population()
    phylo = surface_build_tree(pop)
    assert pfl.alifestd_is_topologically_sorted_polars(phylo)
    assert pfl.alifestd_has_contiguous_ids_polars(phylo)
    assert "hstrat_cross_pair_sum" not in phylo.columns
    assert "hstrat_cross_pair_count" not in phylo.columns
    leaves = phylo.filter(pl.col("dstream_data_id").is_not_null())
    assert len(leaves) == len(pop)
    assert sorted(leaves["td_source_id"]) == sorted(pop["td_source_id"])
    expected = leaves.join(
        pop.select("td_source_id", pl.col("origin_time").alias("td_time")),
        on="td_source_id",
    )
    assert (expected["origin_time"] == expected["td_time"] - 1).all()


def test_trie_postprocessor_applied_after():
    pop = make_population()

    def postprocessor(trie, p_differentia_collision, mutate, progress_wrap):
        if not isinstance(trie, pl.DataFrame):
            raise NotImplementedError
        assert "origin_time" in trie.columns
        return trie.with_columns(foo=pl.lit("bar"))

    phylo = surface_build_tree(pop, trie_postprocessor=postprocessor)
    assert (phylo["foo"] == "bar").all()


def test_no_delete_trunk():
    pop = make_population()
    phylo = surface_build_tree(pop, delete_trunk=False)
    expected = direct_all_pairs_total(pop)
    assert tree_all_pairs_total(phylo) == pytest.approx(expected, rel=1e-9)


def test_empty():
    pop = make_population().head(0)
    phylo = surface_build_tree(pop)
    assert phylo.is_empty()
