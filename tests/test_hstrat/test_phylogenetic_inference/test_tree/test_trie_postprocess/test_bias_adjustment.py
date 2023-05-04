import logging

import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_splay_polytomies,
    alifestd_validate,
    seed_random,
)


@pytest.mark.parametrize("tree_seed", [1, 2, 3])
@pytest.mark.parametrize("tournament_size", [1, 4])
@pytest.mark.parametrize("differentia_width", [1, 2, 8, 64])
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.recency_proportional_resolution_algo.Policy(10),
        # hstrat.depth_proportional_resolution_tapered_algo.Policy(10),
    ],
)
def test_reconstructed_mrca_fuzz(
    tree_seed, tournament_size, differentia_width, retention_policy
):

    seed_random(tree_seed)
    tree = hstrat.evolve_fitness_trait_population(
        population_size=128,
        iter_epochs=False,
        num_islands=1,
        num_niches=1,
        num_generations=256,
        tournament_size=tournament_size,
        p_island_migration=0,
        p_niche_invasion=0,
        share_common_ancestor=True,
    )

    test_population = hstrat.descend_template_phylogeny_alifestd(
        tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
            stratum_differentia_bit_width=differentia_width,
        ),
    )
    control_population = hstrat.descend_template_phylogeny_alifestd(
        tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
            stratum_differentia_bit_width=64,
        ),
    )

    control_df = alifestd_splay_polytomies(
        hstrat.build_tree_trie(control_population)
    )
    assert alifestd_validate(control_df)
    assert alifestd_is_chronologically_ordered(control_df)

    out_dfs = map(
        alifestd_splay_polytomies,
        hstrat.build_tree_trie_ensemble(
            test_population,
            trie_postprocessors=[
                hstrat.AssignOriginTimeNodeRankTriePostprocessor(),
                hstrat.AssignOriginTimeNaiveTriePostprocessor(),
                hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
                    prior=hstrat.ArbitraryPrior(),
                ),
                hstrat.CompoundTriePostprocessor(
                    postprocessors=[
                        hstrat.PeelBackConjoinedLeavesTriePostprocessor(),
                        hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
                            prior=hstrat.ArbitraryPrior()
                        ),
                    ],
                ),
                hstrat.CompoundTriePostprocessor(
                    postprocessors=[
                        hstrat.SampleAncestralRollbacksTriePostprocessor(
                            seed=tree_seed
                        ),
                        hstrat.AssignOriginTimeNaiveTriePostprocessor(),
                    ],
                ),
            ],
        ),
    )

    test_dfs = dict(
        zip(
            ["rank", "naive", "expected", "peeled_expected", "rollback"],
            out_dfs,
        )
    )

    true_mean_origin_time = control_df["origin_time"].mean()
    test_errs = dict()
    for postprocessor, test_df in test_dfs.items():
        assert alifestd_validate(test_df)
        assert alifestd_is_chronologically_ordered(test_df)
        test_mean_origin_time = test_df["origin_time"].mean()
        test_err = test_mean_origin_time - true_mean_origin_time
        test_errs[postprocessor] = test_err
        logging.info(f"{postprocessor} err {test_err}")

    # don't put too much stock into this test...
    # expected/naive should be better than rank most of the time in these tests
    # but not necessarily all the time
    assert abs(test_errs["peeled_expected"]) <= abs(test_errs["expected"])
    assert abs(test_errs["peeled_expected"]) <= abs(test_errs["rank"]) + 0.02
    if differentia_width == 64:
        assert abs(test_errs["naive"]) < abs(test_errs["rank"]) + 0.02
