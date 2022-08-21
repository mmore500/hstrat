import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "policy_t",
    [
        hstrat.depth_proportional_resolution_algo.Policy,
        hstrat.depth_proportional_resolution_tapered_algo.Policy,
        hstrat.fixed_resolution_algo.Policy,
        # disabled because slow
        # hstrat.geom_seq_nth_root_algo.Policy,
        # hstrat.geom_seq_nth_root_tapered_algo.Policy,
        hstrat.recency_proportional_resolution_algo.Policy,
    ],
)
@pytest.mark.parametrize(
    "at_num_strata_deposited",
    [
        10**3,
        10**6,
    ],
)
@pytest.mark.parametrize(
    "target_value",
    [
        1,
        10,
        50,
        100,
    ],
)
def test_satisfiable_at_least(
    policy_t,
    at_num_strata_deposited,
    target_value,
):

    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
        ),
        param_lower_bound=(
            0
            if policy_t == hstrat.recency_proportional_resolution_algo.Policy
            else 1
        ),
    )
    policy_spec = parameterizer(policy_t)
    assert policy_spec == policy_t(parameterizer=parameterizer).GetSpec()

    assert (
        policy_t(policy_spec=policy_spec,).CalcNumStrataRetainedUpperBound(
            at_num_strata_deposited,
        )
        >= target_value
    )

    if policy_t not in (
        hstrat.geom_seq_nth_root_algo.Policy,
        hstrat.geom_seq_nth_root_tapered_algo.Policy,
    ):
        # disable for these policies because too slow
        parameterizer = hstrat.PropertyAtLeastParameterizer(
            target_value=target_value,
            policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
                at_num_strata_deposited=at_num_strata_deposited,
            ),
            param_lower_bound=(
                0
                if policy_t
                == hstrat.recency_proportional_resolution_algo.Policy
                else 1
            ),
            param_upper_bound=None,
        )
        policy_spec = parameterizer(policy_t)
        assert policy_spec == policy_t(parameterizer=parameterizer).GetSpec()

        assert (
            policy_t(policy_spec=policy_spec,).CalcNumStrataRetainedUpperBound(
                at_num_strata_deposited,
            )
            >= target_value
        )


@pytest.mark.parametrize(
    "policy_t",
    [
        hstrat.depth_proportional_resolution_algo.Policy,
        hstrat.depth_proportional_resolution_tapered_algo.Policy,
        hstrat.fixed_resolution_algo.Policy,
        # disabled because slow
        # hstrat.geom_seq_nth_root_algo.Policy,
        # hstrat.geom_seq_nth_root_tapered_algo.Policy,
        hstrat.recency_proportional_resolution_algo.Policy,
    ],
)
@pytest.mark.parametrize(
    "at_num_strata_deposited",
    [
        10**3,
        10**6,
    ],
)
@pytest.mark.parametrize(
    "target_value",
    [
        10**9,
    ],
)
def test_unsatisfiable_at_least(
    policy_t,
    at_num_strata_deposited,
    target_value,
):

    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
        ),
        param_lower_bound=1,
    )
    policy_spec = parameterizer(policy_t)

    assert policy_spec is None
    with pytest.raises(hstrat.UnsatisfiableParameterizationRequestError):
        policy_t(parameterizer=parameterizer)


@pytest.mark.parametrize(
    "policy_t",
    [
        hstrat.depth_proportional_resolution_algo.Policy,
        hstrat.depth_proportional_resolution_tapered_algo.Policy,
        hstrat.fixed_resolution_algo.Policy,
        hstrat.recency_proportional_resolution_algo.Policy,
    ],
)
@pytest.mark.parametrize(
    "at_num_strata_deposited",
    [
        10**3,
        10**6,
    ],
)
@pytest.mark.parametrize(
    "target_value",
    [
        25,
        50,
        100,
        250,
    ],
)
def test_satisfiable_at_most(
    policy_t,
    at_num_strata_deposited,
    target_value,
):

    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
        ),
        param_lower_bound=(
            0
            if policy_t == hstrat.recency_proportional_resolution_algo.Policy
            else 1
        ),
    )
    policy_spec = parameterizer(policy_t)
    assert policy_spec == policy_t(parameterizer=parameterizer).GetSpec()

    assert (
        policy_t(policy_spec=policy_spec,).CalcNumStrataRetainedUpperBound(
            at_num_strata_deposited,
        )
        <= target_value
    )

    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
        ),
        param_lower_bound=(
            0
            if policy_t == hstrat.recency_proportional_resolution_algo.Policy
            else 1
        ),
        param_upper_bound=None,
    )
    policy_spec = parameterizer(policy_t)
    assert policy_spec == policy_t(parameterizer=parameterizer).GetSpec()

    assert (
        policy_t(policy_spec=policy_spec,).CalcNumStrataRetainedUpperBound(
            at_num_strata_deposited,
        )
        <= target_value
    )


@pytest.mark.parametrize(
    "policy_t",
    [
        hstrat.depth_proportional_resolution_algo.Policy,
        hstrat.depth_proportional_resolution_tapered_algo.Policy,
        hstrat.fixed_resolution_algo.Policy,
        # disabled because slow
        # hstrat.geom_seq_nth_root_algo.Policy,
        # hstrat.geom_seq_nth_root_tapered_algo.Policy,
        hstrat.recency_proportional_resolution_algo.Policy,
    ],
)
@pytest.mark.parametrize(
    "at_num_strata_deposited",
    [
        10**3,
        10**6,
    ],
)
@pytest.mark.parametrize(
    "target_value",
    [
        -1,
        0,
        1,
    ],
)
def test_unsatisfiable_at_most(
    policy_t,
    at_num_strata_deposited,
    target_value,
):

    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
        ),
        param_lower_bound=1,
    )
    policy_spec = parameterizer(policy_t)

    assert policy_spec is None
    with pytest.raises(hstrat.UnsatisfiableParameterizationRequestError):
        policy_t(parameterizer=parameterizer)


def test_against_expected_upper_bound():
    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=100,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=100,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=22,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=22,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=21,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=21,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=23,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=4,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=23,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )


def test_against_expected_no_upper_bound():
    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=100,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=100,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=22,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=22,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=21,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=21,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=23,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=4,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=23,
        policy_evaluator=hstrat.NumStrataRetainedUpperBoundEvaluator(
            at_num_strata_deposited=100,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    for __ in range(100):
        assert parameterizer(policy_t) == parameterizer(policy_t)
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )
