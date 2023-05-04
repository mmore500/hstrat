import pytest

from hstrat import hstrat


@pytest.mark.filterwarnings(
    "ignore:Animation was deleted without rendering anything."
)
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
def test_doc_animations(docplot_policy):
    hstrat.stratum_retention_animate(
        docplot_policy,
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
