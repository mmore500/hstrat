from matplotlib import pyplot as plt
import pytest
from slugify import slugify
from teeplot import teeplot as tp

from hstrat import hstrat


# adapted from https://stackoverflow.com/a/61039272
# fixes warning
# Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are
# retained until explicitly closed and may consume too much memory.
def _release_cur_mpl_fig():
    plt.clf()
    plt.close()

@pytest.mark.parametrize(
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(10),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.perfect_resolution_algo.Policy(),
    ],
)
def test(policy):
    hstrat.mrca_uncertainty_absolute_barplot(policy, 100, do_show=False)
    _release_cur_mpl_fig()
    hstrat.mrca_uncertainty_absolute_barplot(policy, 10, do_show=False)
    _release_cur_mpl_fig()


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
def test_docplots(policy):
    tp.tee(
        hstrat.mrca_uncertainty_absolute_barplot,
        policy,
        256,
        teeplot_outattrs={
            "policy": slugify(str(policy)),
            "num_generations": "256",
        },
        teeplot_transparent=False,
    )
    _release_cur_mpl_fig()
