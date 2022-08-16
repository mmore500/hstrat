import numpy as np
import pytest
import sys

from hstrat2 import hstrat

@pytest.mark.parametrize(
    'policy_t',
    [
        hstrat.depth_proportional_resolution_policy.Policy,
        hstrat.depth_proportional_resolution_tapered_policy.Policy,
        hstrat.fixed_resolution_policy.Policy,
        hstrat.geom_seq_nth_root_policy.Policy,
        hstrat.geom_seq_nth_root_tapered_policy.Policy,
        hstrat.recency_proportional_resolution_policy.Policy,
    ],
)
@pytest.mark.parametrize(
    'at_num_strata_deposited',
    [
        10**3,
        10**6,
    ],
)
@pytest.mark.parametrize(
    'at_rank',
    [
        None,
        -1,
        -8,
        0,
        100,
    ],
)
@pytest.mark.parametrize(
    'target_value',
    [
        0.01,
        0.25,
        1,
    ],
)
def test_satisfiable(
    policy_t,
    at_num_strata_deposited,
    at_rank,
    target_value,
):

    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.MrcaUncertaintyRelUpperBoundPolicyEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
            at_rank=at_rank,
        ),
        param_lower_bound=1,
    )
    policy_spec = parameterizer(policy_t)
    assert policy_spec == policy_t(parameterizer=parameterizer).GetSpec()

    if at_rank is not None:
        assert policy_t(
            policy_spec=policy_spec,
        ).CalcMrcaUncertaintyRelUpperBound(
            at_num_strata_deposited,
            at_num_strata_deposited,
            at_rank,
        ) >= target_value
    else:
        assert policy_t(
            policy_spec=policy_spec,
        ).CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
            at_num_strata_deposited,
            at_num_strata_deposited,
        ) >= target_value

    if policy_t not in (
        hstrat.geom_seq_nth_root_policy.Policy,
        hstrat.geom_seq_nth_root_tapered_policy.Policy,
    ):
        # disable for these policies because too slow
        parameterizer = hstrat.PropertyAtLeastParameterizer(
            target_value=target_value,
            policy_evaluator=hstrat.MrcaUncertaintyRelUpperBoundPolicyEvaluator(
                at_num_strata_deposited=at_num_strata_deposited,
                at_rank=at_rank,
            ),
            param_lower_bound=1,
            param_upper_bound=None,
        )
        policy_spec = parameterizer(policy_t)
        assert policy_spec == policy_t(parameterizer=parameterizer).GetSpec()

        if at_rank is not None:
            assert policy_t(
                policy_spec=policy_spec,
            ).CalcMrcaUncertaintyRelUpperBound(
                at_num_strata_deposited,
                at_num_strata_deposited,
                at_rank,
            ) >= target_value
        else:
            assert policy_t(
                policy_spec=policy_spec,
            ).CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
                at_num_strata_deposited,
                at_num_strata_deposited,
            ) >= target_value

@pytest.mark.parametrize(
    'policy_t',
    [
        hstrat.depth_proportional_resolution_policy.Policy,
        hstrat.depth_proportional_resolution_tapered_policy.Policy,
        hstrat.fixed_resolution_policy.Policy,
        hstrat.geom_seq_nth_root_policy.Policy,
        hstrat.geom_seq_nth_root_tapered_policy.Policy,
        hstrat.recency_proportional_resolution_policy.Policy,
    ],
)
@pytest.mark.parametrize(
    'at_num_strata_deposited',
    [
        10**3,
        10**6,
    ],
)
@pytest.mark.parametrize(
    'at_rank,target_value',
    [
        (None, 10**9),
        (-1, 10**9),
        (-8, 10**9),
        (0, 1.01),
        (10, 1.1),
    ],
)
def test_unsatisfiable(
    policy_t,
    at_num_strata_deposited,
    at_rank,
    target_value,
):

    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.MrcaUncertaintyRelUpperBoundPolicyEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
            at_rank=at_rank,
        ),
        param_lower_bound=1,
    )
    policy_spec = parameterizer(policy_t)

    assert policy_spec is None
    with pytest.raises(hstrat.UnsatisfiableParameterizationRequestError):
        policy_t(parameterizer=parameterizer)

    if policy_t not in (
        hstrat.geom_seq_nth_root_policy.Policy,
        hstrat.geom_seq_nth_root_tapered_policy.Policy,
    ):
        # disable for these policies because too slow
        parameterizer = hstrat.PropertyAtLeastParameterizer(
            target_value=target_value,
            policy_evaluator=hstrat.MrcaUncertaintyRelUpperBoundPolicyEvaluator(
                at_num_strata_deposited=at_num_strata_deposited,
                at_rank=at_rank,
            ),
            param_lower_bound=1,
            param_upper_bound=None,
        )
        policy_spec = parameterizer(policy_t)

        assert policy_spec is None
        with pytest.raises(hstrat.UnsatisfiableParameterizationRequestError):
            policy_t(parameterizer=parameterizer)
