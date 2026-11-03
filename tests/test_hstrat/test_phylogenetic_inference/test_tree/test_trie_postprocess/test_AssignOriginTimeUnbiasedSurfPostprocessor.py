import functools
import itertools
import os
import typing

from downstream import dstream
import numpy as np
from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import ExperimentalWarning, seed_random
from hstrat.dataframe import surface_build_tree as surface_build_tree_naive
from hstrat.dataframe import surface_test_drive

assets = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../test_dataframe/assets",
)


def surface_build_tree(df: pl.DataFrame, **kwargs) -> pl.DataFrame:
    """Build tree with unbiased origin times."""
    return surface_build_tree_naive(
        df,
        trie_postprocessor=hstrat.AssignOriginTimeUnbiasedSurfPostprocessor(
            **kwargs
        ),
    )


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


def _calc_cherry_errors(
    phylo: pl.DataFrame, true_split_times: typing.List[int]
) -> np.ndarray:
    """Estimated minus true divergence time, for each cherry's tip pair."""
    ancestor_ids = phylo["ancestor_id"].to_numpy()
    origin_times = phylo["origin_time"].to_numpy()
    leaf_ids = {
        source_id: id_
        for id_, source_id in enumerate(phylo["td_source_id"])
        if source_id is not None
    }

    def lineage(id_: int) -> typing.List[int]:
        lineage = [id_]
        while ancestor_ids[lineage[-1]] != lineage[-1]:
            lineage.append(ancestor_ids[lineage[-1]])
        return lineage

    errors = []
    for k, true_split_time in enumerate(true_split_times):
        lineage_a = lineage(leaf_ids[3 * k + 2])
        lineage_b = {*lineage(leaf_ids[3 * k + 3])}
        mrca_id = next((id_ for id_ in lineage_a if id_ in lineage_b), None)
        if mrca_id is not None:  # split before first shared rank otherwise
            errors.append(origin_times[mrca_id] - true_split_time)
    return np.array(errors)


@pytest.mark.parametrize(
    "algo", ["steady_algo", "tilted_algo", "hybrid_0_steady_1_tilted_2_algo"]
)
def test_origin_times_unbiased(algo: str):
    # many independent cherries under a common root: root (generation 0)
    # <- split (generation T) <- two tips (generation G)
    seed_random(1)
    S, G, num_cherries = 16, 200, 400
    # test drive deposits S items before founding, so ranks are offset by S
    retained = np.sort(
        getattr(dstream, algo).lookup_ingest_times_batched(
            S, np.array([G + S], dtype=np.uint64), parallel=False
        )[0],
    )
    first_shared = retained[retained >= S][0] - S
    split_times = np.random.randint(first_shared, G - 1, size=num_cherries)
    true_df = pl.DataFrame(
        {
            "id": np.arange(3 * num_cherries + 1),
            "ancestor_id": [
                0,
                *itertools.chain(
                    *((0, k, k) for k in range(1, 3 * num_cherries, 3))
                ),
            ],
            "origin_time": [
                0,
                *itertools.chain(*((T, G, G) for T in split_times)),
            ],
        },
    ).cast(pl.UInt64)
    tips_df = surface_test_drive(
        true_df.lazy(),
        dstream_algo=f"dstream.{algo}",
        dstream_S=S,
        stratum_differentia_bit_width=1,
    )

    corrected = _calc_cherry_errors(
        surface_build_tree(tips_df),
        split_times.tolist(),
    )
    uncorrected = _calc_cherry_errors(
        surface_build_tree_naive(tips_df).with_columns(
            origin_time=pl.col("hstrat_rank"),
        ),
        split_times.tolist(),
    )

    standard_error = corrected.std() / np.sqrt(len(corrected))
    assert len(corrected) >= 0.99 * num_cherries
    assert abs(corrected.mean()) < 3 * standard_error
    # without correction, estimates are biased toward being too recent
    assert uncorrected.mean() - corrected.mean() > 3 * standard_error


@pytest.mark.parametrize(
    "dstream_algo", ["dstream.steady_algo", "dstream.tilted_algo"]
)
@pytest.mark.parametrize("bitwidth", [1, 8])
def test_topology_unchanged(dstream_algo: str, bitwidth: int):
    pop = make_population(dstream_algo, 64, bitwidth)
    phylo = surface_build_tree(pop)
    naive = surface_build_tree_naive(pop)
    assert phylo.select("id", "ancestor_id", "hstrat_rank").equals(
        naive.select("id", "ancestor_id", "hstrat_rank"),
    )


def test_tree_shape():
    pop = make_population()
    phylo = surface_build_tree(pop)
    assert pfl.alifestd_is_topologically_sorted_polars(phylo)
    assert pfl.alifestd_has_contiguous_ids_polars(phylo)
    leaves = phylo.filter(pl.col("dstream_data_id").is_not_null())
    assert len(leaves) == len(pop)
    expected = leaves.join(
        pop.select("td_source_id", pl.col("origin_time").alias("td_time")),
        on="td_source_id",
    )
    assert (expected["origin_time"] == expected["td_time"] - 1).all()


def test_no_delete_trunk():
    pop = make_population()
    phylo = surface_build_tree_naive(
        pop,
        delete_trunk=False,
        trie_postprocessor=hstrat.AssignOriginTimeUnbiasedSurfPostprocessor(),
    )
    assert phylo["origin_time"].is_finite().all()


def test_polars_only():
    postprocessor = hstrat.AssignOriginTimeUnbiasedSurfPostprocessor()
    trie = pl.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "rank": [64],
            "dstream_S": [64],
            "dstream_algo": ["dstream.steady_algo"],
        },
    )
    with pytest.raises(NotImplementedError):
        postprocessor(trie.to_pandas(), p_differentia_collision=0.5)
    assert postprocessor(trie, p_differentia_collision=0.5)[
        "origin_time"
    ].to_list() == [0.0]


def test_experimental_warning(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("HSTRAT_WARN_EXPERIMENTAL_SUPPRESS", raising=False)
    with pytest.warns(ExperimentalWarning):
        hstrat.AssignOriginTimeUnbiasedSurfPostprocessor()
