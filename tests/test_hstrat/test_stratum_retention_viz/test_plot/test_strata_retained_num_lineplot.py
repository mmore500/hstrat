import pytest
from slugify import slugify
from teeplot import teeplot as tp

from hstrat import hstrat
from hstrat._auxiliary_lib import release_cur_mpl_fig


@pytest.mark.parametrize(
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(10),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.perfect_resolution_algo.Policy(),
    ],
)
def test(policy):
    hstrat.strata_retained_num_lineplot(policy, 100, do_show=False)
    release_cur_mpl_fig()
    hstrat.strata_retained_num_lineplot(policy, 10, do_show=False)
    release_cur_mpl_fig()


@pytest.mark.heavy
def test_docplots(docplot_policy):
    tp.tee(
        hstrat.strata_retained_num_lineplot,
        docplot_policy,
        256,
        teeplot_outattrs={
            "policy": slugify(str(docplot_policy)),
            "num_generations": "256",
        },
        teeplot_transparent=False,
    )
    release_cur_mpl_fig()
