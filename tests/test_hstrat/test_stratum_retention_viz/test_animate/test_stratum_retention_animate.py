import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "policy",
    [
        hstrat.geom_seq_nth_root_algo.Policy(4),
    ],
)
def test_one(policy):
    hstrat.stratum_retention_animate(
        policy,
        10,
        draw_extant_history=False,
        draw_extinct_history=False,
        draw_extinct_placeholders=True,
    ).to_html5_video(
        embed_limit=0
    )  # silence mpl unused animation warning
    hstrat.stratum_retention_animate(
        policy,
        10,
        draw_extant_history=True,
        draw_extinct_history=False,
        draw_extinct_placeholders=True,
    ).to_html5_video(
        embed_limit=0
    )  # silence mpl unused animation warning
    hstrat.stratum_retention_animate(policy, 10).to_html5_video(
        embed_limit=0
    )  # silence mpl unused animation warning


@pytest.mark.heavy
@pytest.mark.parametrize(
    "policy",
    [
        policy_t(
            parameterizer=hstrat.PropertyExactlyParameterizer(
                target_value=target_value,
                policy_evaluator=hstrat.MrcaUncertaintyAbsExactEvaluator(
                    at_num_strata_deposited=256,
                    at_rank=0,
                ),
                param_lower_bound=lb,
                param_upper_bound=1024,
            )
        )
        for policy_t, lb in (
            (hstrat.fixed_resolution_algo.Policy, 1),
            (hstrat.depth_proportional_resolution_algo.Policy, 1),
            (hstrat.depth_proportional_resolution_tapered_algo.Policy, 1),
            (hstrat.recency_proportional_resolution_algo.Policy, 0),
        )
        for target_value in (31, 127)
    ]
    + [
        policy_t(
            parameterizer=hstrat.PropertyAtLeastParameterizer(
                target_value=31,
                policy_evaluator=hstrat.MrcaUncertaintyAbsExactEvaluator(
                    at_num_strata_deposited=256,
                    at_rank=0,
                ),
                param_lower_bound=1,
                param_upper_bound=1024,
            )
        )
        for policy_t in (
            hstrat.geom_seq_nth_root_algo.Policy,
            hstrat.geom_seq_nth_root_tapered_algo.Policy,
        )
    ]
    + [
        hstrat.geom_seq_nth_root_algo.Policy(
            parameterizer=hstrat.PropertyExactlyParameterizer(
                target_value=127,
                policy_evaluator=hstrat.MrcaUncertaintyAbsExactEvaluator(
                    at_num_strata_deposited=256,
                    at_rank=0,
                ),
                param_lower_bound=1,
                param_upper_bound=1024,
            )
        )
    ]
    + [
        hstrat.geom_seq_nth_root_tapered_algo.Policy(
            parameterizer=hstrat.PropertyAtMostParameterizer(
                target_value=127,
                policy_evaluator=hstrat.MrcaUncertaintyAbsExactEvaluator(
                    at_num_strata_deposited=256,
                    at_rank=0,
                ),
                param_lower_bound=1,
                param_upper_bound=1024,
            )
        )
    ],
)
def test_doc_animations(policy):
    hstrat.stratum_retention_animate(
        policy,
        256,
        save_as="gif",
    )


@pytest.mark.heavy
@pytest.mark.parametrize(
    "policy",
    [
        hstrat.depth_proportional_resolution_tapered_algo.Policy(
            parameterizer=hstrat.PropertyAtMostParameterizer(
                target_value=10,
                policy_evaluator=hstrat.NumStrataRetainedExactEvaluator(
                    at_num_strata_deposited=256,
                ),
                param_lower_bound=1,
                param_upper_bound=1024,
            )
        )
    ],
)
def test_more_doc_animations(policy):

    hstrat.stratum_retention_animate(
        policy,
        256,
        draw_extant_history=False,
        draw_extinct_history=False,
        draw_extinct_placeholders=True,
        save_as="gif",
    )
    hstrat.stratum_retention_animate(
        policy,
        256,
        draw_extant_history=True,
        draw_extinct_history=False,
        draw_extinct_placeholders=True,
        save_as="gif",
    )
    hstrat.stratum_retention_animate(
        policy,
        256,
        save_as="gif",
    )
