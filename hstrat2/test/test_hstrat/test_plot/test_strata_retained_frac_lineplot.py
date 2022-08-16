import pytest
from slugify import slugify
from teeplot import teeplot as tp

from hstrat2 import hstrat


@pytest.mark.parametrize(
    'policy',
    [
        hstrat.fixed_resolution_policy.Policy(10),
        hstrat.nominal_resolution_policy.Policy(),
        hstrat.perfect_resolution_policy.Policy(),
    ],
)
def test(policy):
    hstrat.strata_retained_frac_lineplot(policy, 100, do_show=False)
    hstrat.strata_retained_frac_lineplot(policy, 10, do_show=False)

@pytest.mark.parametrize(
    'policy',
    [
        policy_t(
            parameterizer=hstrat.PropertyExactlyParameterizer(
                target_value=target_value,
                policy_evaluator \
                    =hstrat.MrcaUncertaintyAbsExactPolicyEvaluator(
                        at_num_strata_deposited=256,
                        at_rank=0,
                ),
                param_lower_bound=lb,
                param_upper_bound=1024,
            )
        )
        for policy_t, lb in (
            (hstrat.fixed_resolution_policy.Policy, 1),
            (hstrat.depth_proportional_resolution_policy.Policy, 1),
            (hstrat.depth_proportional_resolution_tapered_policy.Policy, 1),
            (hstrat.recency_proportional_resolution_policy.Policy, 0),
        )
        for target_value in (31, 127)
    ] + [
        policy_t(
            parameterizer=hstrat.PropertyAtLeastParameterizer(
                target_value=31,
                policy_evaluator \
                    =hstrat.MrcaUncertaintyAbsExactPolicyEvaluator(
                        at_num_strata_deposited=256,
                        at_rank=0,
                ),
                param_lower_bound=1,
                param_upper_bound=1024,
            )
        )
        for policy_t in (
            hstrat.geom_seq_nth_root_policy.Policy,
            hstrat.geom_seq_nth_root_tapered_policy.Policy,
        )
    ] + [
        hstrat.geom_seq_nth_root_policy.Policy(
            parameterizer=hstrat.PropertyExactlyParameterizer(
                target_value=127,
                policy_evaluator \
                    =hstrat.MrcaUncertaintyAbsExactPolicyEvaluator(
                        at_num_strata_deposited=256,
                        at_rank=0,
                ),
                param_lower_bound=1,
                param_upper_bound=1024,
            )
        )
    ] + [
        hstrat.geom_seq_nth_root_tapered_policy.Policy(
            parameterizer=hstrat.PropertyAtMostParameterizer(
                target_value=127,
                policy_evaluator \
                    =hstrat.MrcaUncertaintyAbsExactPolicyEvaluator(
                        at_num_strata_deposited=256,
                        at_rank=0,
                ),
                param_lower_bound=1,
                param_upper_bound=1024,
            )
        )
    ]
)
def test_docplots(policy):
    tp.tee(
        hstrat.strata_retained_frac_lineplot,
        policy,
        256,
        teeplot_outattrs={
            'policy' : slugify(str(policy)),
            'num_generations' : '256',
        },
    )
