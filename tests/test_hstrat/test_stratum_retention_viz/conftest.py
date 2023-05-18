import pytest

from hstrat import hstrat


@pytest.fixture(
    params=[
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
            hstrat.recency_proportional_resolution_curbed_algo.Policy,
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
        hstrat.recency_proportional_resolution_curbed_algo.Policy(
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
        hstrat.recency_proportional_resolution_curbed_algo.Policy(
            size_curb=8,
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
def docplot_policy(request):
    return request.param
