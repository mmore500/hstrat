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
    hstrat.policy_panel_animate(policy, 10,).to_html5_video(
        embed_limit=0
    )  # silence mpl unused animation warning


@pytest.mark.heavy
def test_doc_animations(docplot_policy):
    hstrat.policy_panel_animate(
        docplot_policy,
        256,
        save_as="gif",
    )
