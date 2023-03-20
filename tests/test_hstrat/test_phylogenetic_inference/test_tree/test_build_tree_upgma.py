import os

import pytest

from hstrat import hstrat

from . import _impl as impl

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "orig_tree",
    [
        pytest.param(
            impl.setup_dendropy_tree(f"{assets_path}/nk_ecoeaselection.csv"),
            marks=pytest.mark.heavy,
        ),
        impl.setup_dendropy_tree(f"{assets_path}/nk_lexicaseselection.csv"),
        impl.setup_dendropy_tree(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.recency_proportional_resolution_algo.Policy(3),
        hstrat.fixed_resolution_algo.Policy(5),
    ],
)
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        hstrat.col_to_specimen,
    ],
)
@pytest.mark.parametrize(
    "estimator",
    [
        "maximum_likelihood",
        "unbiased",
    ],
)
@pytest.mark.parametrize(
    "prior",
    [
        "arbitrary",
        "uniform",
        hstrat.ExponentialPrior(1.01),
    ],
)
def test_determinism(orig_tree, retention_policy, wrap, estimator, prior):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )

    first_reconst = hstrat.build_tree_upgma(
        extant_population, estimator, prior
    )
    for _rep in range(3):
        _ = _rep
        second_reconst = hstrat.build_tree_upgma(
            [wrap(col) for col in extant_population],
            estimator,
            prior,
        )
        assert first_reconst.equals(second_reconst)


@pytest.mark.parametrize(
    "orig_tree",
    [
        impl.setup_dendropy_tree(f"{assets_path}/nk_lexicaseselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.recency_proportional_resolution_algo.Policy(4),
    ],
)
def test_reconstructed_taxon_labels(orig_tree, retention_policy):
    num_depositions = 10

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        orig_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ).CloneNthDescendant(num_depositions),
    )
    taxon_labels = [str(id(x)) for x in extant_population]

    reconst_df = hstrat.build_tree_upgma(
        extant_population,
        "maximum_likelihood",
        "arbitrary",
        taxon_labels=taxon_labels,
    )
    assert "taxon_label" in reconst_df
    assert set(taxon_labels) < set(reconst_df["taxon_label"])

    reconst_df = hstrat.build_tree_upgma(
        extant_population,
        "maximum_likelihood",
        "arbitrary",
    )
    assert "taxon_label" in reconst_df
    assert len(reconst_df["taxon_label"].unique()) == len(
        reconst_df["taxon_label"]
    )
    assert set(map(str, range(len(extant_population)))) < set(
        reconst_df["taxon_label"]
    )
