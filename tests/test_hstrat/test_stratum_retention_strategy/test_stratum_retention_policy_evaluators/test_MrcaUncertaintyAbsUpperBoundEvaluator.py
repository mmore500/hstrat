import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "policy_t",
    [
        hstrat.depth_proportional_resolution_algo.Policy,
        hstrat.depth_proportional_resolution_tapered_algo.Policy,
        hstrat.fixed_resolution_algo.Policy,
        hstrat.geom_seq_nth_root_algo.Policy,
        hstrat.geom_seq_nth_root_tapered_algo.Policy,
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
    "at_rank",
    [
        None,
        -1,
        -8,
        0,
        100,
    ],
)
@pytest.mark.parametrize(
    "target_value",
    [
        1,
        10,
        50,
        100,
        500,
    ],
)
def test_satisfiable_at_least(
    policy_t,
    at_num_strata_deposited,
    at_rank,
    target_value,
):

    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
            at_rank=at_rank,
        ),
        param_lower_bound=(
            0
            if policy_t == hstrat.recency_proportional_resolution_algo.Policy
            else 1
        ),
    )
    policy_spec = parameterizer(policy_t)
    assert policy_spec == policy_t(parameterizer=parameterizer).GetSpec()

    if at_rank is not None:
        assert (
            policy_t(
                policy_spec=policy_spec,
            ).CalcMrcaUncertaintyAbsUpperBound(
                at_num_strata_deposited,
                at_num_strata_deposited,
                at_rank,
            )
            >= target_value
        )
    else:
        assert (
            policy_t(
                policy_spec=policy_spec,
            ).CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
                at_num_strata_deposited,
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
            policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
                at_num_strata_deposited=at_num_strata_deposited,
                at_rank=at_rank,
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

        if at_rank is not None:
            assert (
                policy_t(
                    policy_spec=policy_spec,
                ).CalcMrcaUncertaintyAbsUpperBound(
                    at_num_strata_deposited,
                    at_num_strata_deposited,
                    at_rank,
                )
                >= target_value
            )
        else:
            assert (
                policy_t(
                    policy_spec=policy_spec,
                ).CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
                    at_num_strata_deposited,
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
        hstrat.geom_seq_nth_root_algo.Policy,
        hstrat.geom_seq_nth_root_tapered_algo.Policy,
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
    "at_rank,target_value",
    [
        (None, 10**7),
        (-1, 10**7),
        (-8, 10**7),
        (0, 10**7),
        (10, 10**7),
    ],
)
def test_unsatisfiable_at_least(
    policy_t,
    at_num_strata_deposited,
    at_rank,
    target_value,
):

    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
            at_rank=at_rank,
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
    "at_rank",
    [
        None,
        -1,
        -8,
        0,
        100,
    ],
)
@pytest.mark.parametrize(
    "target_value",
    [
        1,
        50,
        250,
    ],
)
def test_satisfiable_at_most(
    policy_t,
    at_num_strata_deposited,
    at_rank,
    target_value,
):

    if (
        policy_t
        not in (
            hstrat.geom_seq_nth_root_algo.Policy,
            hstrat.geom_seq_nth_root_tapered_algo.Policy,
        )
        or target_value > 1
    ):
        parameterizer = hstrat.PropertyAtMostParameterizer(
            target_value=target_value,
            policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
                at_num_strata_deposited=at_num_strata_deposited,
                at_rank=at_rank,
            ),
            param_lower_bound=1,
        )
        policy_spec = parameterizer(policy_t)
        assert policy_spec == policy_t(parameterizer=parameterizer).GetSpec()

        if at_rank is not None:
            assert (
                policy_t(
                    policy_spec=policy_spec,
                ).CalcMrcaUncertaintyAbsUpperBound(
                    at_num_strata_deposited,
                    at_num_strata_deposited,
                    at_rank,
                )
                <= target_value
            )
        else:
            assert (
                policy_t(
                    policy_spec=policy_spec,
                ).CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
                    at_num_strata_deposited,
                    at_num_strata_deposited,
                )
                <= target_value
            )

    if policy_t not in (
        hstrat.geom_seq_nth_root_algo.Policy,
        hstrat.geom_seq_nth_root_tapered_algo.Policy,
    ):
        parameterizer = hstrat.PropertyAtMostParameterizer(
            target_value=target_value,
            policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
                at_num_strata_deposited=at_num_strata_deposited,
                at_rank=at_rank,
            ),
            param_lower_bound=1,
            param_upper_bound=None,
        )
        policy_spec = parameterizer(policy_t)
        assert policy_spec == policy_t(parameterizer=parameterizer).GetSpec()

        if at_rank is not None:
            assert (
                policy_t(
                    policy_spec=policy_spec,
                ).CalcMrcaUncertaintyAbsUpperBound(
                    at_num_strata_deposited,
                    at_num_strata_deposited,
                    at_rank,
                )
                <= target_value
            )
        else:
            assert (
                policy_t(
                    policy_spec=policy_spec,
                ).CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
                    at_num_strata_deposited,
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
        hstrat.geom_seq_nth_root_algo.Policy,
        hstrat.geom_seq_nth_root_tapered_algo.Policy,
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
    "at_rank,target_value",
    [
        (None, -1),
        (-1, -1),
        (-8, -1),
        (0, -1),
        (10, -1),
    ],
)
def test_unsatisfiable_at_most(
    policy_t,
    at_num_strata_deposited,
    at_rank,
    target_value,
):

    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=target_value,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=at_num_strata_deposited,
            at_rank=at_rank,
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
        target_value=0,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=100,
            at_rank=0,
        ),
        param_lower_bound=1,
    )
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=0,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=98,
        ),
        param_lower_bound=1,
    )
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=0,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=100,
            at_rank=0,
        ),
        param_lower_bound=1,
    )
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=0,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=98,
        ),
        param_lower_bound=1,
    )
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=4.5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=4.5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=5.5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=7,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=5.5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )


def test_against_expected_no_upper_bound():

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=0,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=100,
            at_rank=0,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=0,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=98,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=0,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=100,
            at_rank=0,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=0,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=98,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    assert parameterizer(policy_t) == policy_t.policy_spec_t(
        fixed_resolution=1,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=4.5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=4.5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=5,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtLeastParameterizer(
        target_value=5.5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=7,
    )

    # case
    policy_t = hstrat.fixed_resolution_algo.Policy
    parameterizer = hstrat.PropertyAtMostParameterizer(
        target_value=5.5,
        policy_evaluator=hstrat.MrcaUncertaintyAbsUpperBoundEvaluator(
            at_num_strata_deposited=101,
            at_rank=0,
        ),
        param_lower_bound=1,
        param_upper_bound=None,
    )
    res_spec = parameterizer(policy_t)
    assert res_spec == policy_t.policy_spec_t(
        fixed_resolution=6,
    )
