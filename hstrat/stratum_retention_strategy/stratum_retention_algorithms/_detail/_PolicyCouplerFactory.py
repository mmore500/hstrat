import typing

import opytional as opyt

from .._impl import (
    CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
    CalcMrcaUncertaintyAbsUpperBoundPessimalRankBruteForce,
    CalcMrcaUncertaintyAbsUpperBoundWorstCase,
    CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
    CalcMrcaUncertaintyRelUpperBoundPessimalRankBruteForce,
    CalcMrcaUncertaintyRelUpperBoundWorstCase,
    CalcNumStrataRetainedUpperBoundWorstCase,
)
from ._PolicyCouplerBase import PolicyCouplerBase
from ._PolicySpecBase import PolicySpecBase
from ._UnsatisfiableParameterizationRequestError import (
    UnsatisfiableParameterizationRequestError,
)


class _CurryPolicy:
    """Helper class to enable the policy coupler to insert itself as the
    first argument to calls to implementation functors."""

    _policy: PolicyCouplerBase
    _ftor: typing.Callable

    def __init__(
        self: "_CurryPolicy",
        policy: PolicyCouplerBase,
        ftor: typing.Callable,
    ) -> None:
        self._policy = policy
        self._ftor = ftor

    def __eq__(self: "_CurryPolicy", other: typing.Any) -> bool:
        return isinstance(other, self.__class__) and (
            # don't compare policy to prevent infinite recursion
            self._ftor
            == other._ftor,
        )

    def __call__(self: "_CurryPolicy", *args, **kwargs) -> typing.Any:
        return self._ftor(self._policy, *args, **kwargs)


_ftor_type = typing.Type[typing.Callable]


def PolicyCouplerFactory(
    *,
    policy_spec_t: typing.Type,
    # enactment
    gen_drop_ranks_ftor_t: _ftor_type,
    # invariants
    calc_mrca_uncertainty_abs_upper_bound_ftor_t: _ftor_type = CalcMrcaUncertaintyAbsUpperBoundWorstCase,
    calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor_t: _ftor_type = CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
    calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor_t: _ftor_type = CalcMrcaUncertaintyAbsUpperBoundPessimalRankBruteForce,
    calc_mrca_uncertainty_rel_upper_bound_ftor_t: _ftor_type = CalcMrcaUncertaintyRelUpperBoundWorstCase,
    calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor_t: _ftor_type = CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
    calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor_t: _ftor_type = CalcMrcaUncertaintyRelUpperBoundPessimalRankBruteForce,
    calc_num_strata_retained_upper_bound_ftor_t: _ftor_type = CalcNumStrataRetainedUpperBoundWorstCase,
    # scrying
    calc_mrca_uncertainty_abs_exact_ftor_t: typing.Optional[_ftor_type] = None,
    calc_mrca_uncertainty_rel_exact_ftor_t: typing.Optional[_ftor_type] = None,
    calc_num_strata_retained_exact_ftor_t: typing.Optional[_ftor_type] = None,
    calc_rank_at_column_index_ftor_t: typing.Optional[_ftor_type] = None,
    iter_retained_ranks_ftor_t: typing.Optional[_ftor_type] = None,
) -> typing.Type[typing.Callable]:
    """Joins policy implementation functors into a single class that can be
    instantiated with particular policy specification parameters."""
    policy_spec_t_ = policy_spec_t

    class PolicyCoupler(
        PolicyCouplerBase,
    ):
        """Instantiate policy implementation for particular policy
        specification parameters."""

        _policy_spec: policy_spec_t_

        # invariants
        CalcMrcaUncertaintyAbsUpperBound: typing.Callable
        CalcMrcaUncertaintyAbsUpperBoundPessimalRank: typing.Callable
        CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank: typing.Callable
        CalcMrcaUncertaintyRelUpperBound: typing.Callable
        CalcMrcaUncertaintyRelUpperBoundAtPessimalRank: typing.Callable
        CalcMrcaUncertaintyRelUpperBoundPessimalRank: typing.Callable
        CalcNumStrataRetainedUpperBound: typing.Callable

        # scrying
        CalcMrcaUncertaintyAbsExact: typing.Optional[typing.Callable]
        CalcMrcaUncertaintyRelExact: typing.Optional[typing.Callable]
        CalcNumStrataRetainedExact: typing.Optional[typing.Callable]
        CalcRankAtColumnIndex: typing.Optional[typing.Callable]
        IterRetainedRanks: typing.Optional[typing.Callable]

        # enactment
        GenDropRanks: typing.Callable

        policy_spec_t: typing.Type = policy_spec_t_

        def __init__(
            self: "PolicyCoupler",
            *args,
            parameterizer: typing.Optional[
                typing.Callable[[typing.Type], typing.Optional[PolicySpecBase]]
            ] = None,
            policy_spec: typing.Optional[PolicySpecBase] = None,
            **kwargs,
        ):
            """Construct a PolicyCoupler instance.

            If policy_spec is not provided, all arguments are forwarded to
            policy spec initializer.
            """
            if policy_spec is not None:
                assert len(args) == len(kwargs) == 0
                assert parameterizer is None
                self._policy_spec = policy_spec
            elif parameterizer is not None:
                assert len(args) == len(kwargs) == 0
                assert policy_spec is None
                maybe_policy_spec = parameterizer(type(self))
                if maybe_policy_spec is None:
                    raise UnsatisfiableParameterizationRequestError(
                        repr(type(self)),
                        repr(parameterizer),
                    )
                else:
                    self._policy_spec = maybe_policy_spec
            else:
                assert parameterizer is None
                assert policy_spec is None
                self._policy_spec = policy_spec_t_(*args, **kwargs)

            # enactment
            self.GenDropRanks = _CurryPolicy(
                self,
                gen_drop_ranks_ftor_t(self._policy_spec),
            )

            # invariants
            self.CalcMrcaUncertaintyAbsUpperBound = _CurryPolicy(
                self,
                calc_mrca_uncertainty_abs_upper_bound_ftor_t(
                    self._policy_spec
                ),
            )
            self.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank = _CurryPolicy(
                self,
                calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor_t(
                    self._policy_spec,
                ),
            )
            self.CalcMrcaUncertaintyAbsUpperBoundPessimalRank = _CurryPolicy(
                self,
                calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor_t(
                    self._policy_spec,
                ),
            )
            self.CalcMrcaUncertaintyRelUpperBound = _CurryPolicy(
                self,
                calc_mrca_uncertainty_rel_upper_bound_ftor_t(
                    self._policy_spec
                ),
            )
            self.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank = _CurryPolicy(
                self,
                calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor_t(
                    self._policy_spec
                ),
            )
            self.CalcMrcaUncertaintyRelUpperBoundPessimalRank = _CurryPolicy(
                self,
                calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor_t(
                    self._policy_spec
                ),
            )
            self.CalcNumStrataRetainedUpperBound = _CurryPolicy(
                self,
                calc_num_strata_retained_upper_bound_ftor_t(self._policy_spec),
            )

            # scrying
            self.CalcMrcaUncertaintyAbsExact = opyt.apply_if(
                calc_mrca_uncertainty_abs_exact_ftor_t,
                lambda x: _CurryPolicy(self, x(self._policy_spec)),
            )
            self.CalcMrcaUncertaintyRelExact = opyt.apply_if(
                calc_mrca_uncertainty_rel_exact_ftor_t,
                lambda x: _CurryPolicy(self, x(self._policy_spec)),
            )
            self.CalcNumStrataRetainedExact = opyt.apply_if(
                calc_num_strata_retained_exact_ftor_t,
                lambda x: _CurryPolicy(self, x(self._policy_spec)),
            )
            self.CalcRankAtColumnIndex = opyt.apply_if(
                calc_rank_at_column_index_ftor_t,
                lambda x: _CurryPolicy(self, x(self._policy_spec)),
            )
            self.IterRetainedRanks = opyt.apply_if(
                iter_retained_ranks_ftor_t,
                lambda x: _CurryPolicy(self, x(self._policy_spec)),
            )

        def __eq__(
            self: "PolicyCoupler",
            other: typing.Any,
        ) -> bool:
            if issubclass(
                other.__class__,
                PolicyCouplerBase,
            ):
                return (
                    self._policy_spec,
                    self.GenDropRanks,
                    self.CalcMrcaUncertaintyAbsUpperBound,
                    self.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
                    self.CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
                    self.CalcMrcaUncertaintyRelUpperBound,
                    self.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
                    self.CalcMrcaUncertaintyRelUpperBoundPessimalRank,
                    self.CalcNumStrataRetainedUpperBound,
                    self.CalcMrcaUncertaintyAbsExact,
                    self.CalcMrcaUncertaintyRelExact,
                    self.CalcNumStrataRetainedExact,
                    self.CalcRankAtColumnIndex,
                    self.IterRetainedRanks,
                ) == (
                    other._policy_spec,
                    other.GenDropRanks,
                    other.CalcMrcaUncertaintyAbsUpperBound,
                    other.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
                    other.CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
                    other.CalcMrcaUncertaintyRelUpperBound,
                    other.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
                    other.CalcMrcaUncertaintyRelUpperBoundPessimalRank,
                    other.CalcNumStrataRetainedUpperBound,
                    other.CalcMrcaUncertaintyAbsExact,
                    other.CalcMrcaUncertaintyRelExact,
                    other.CalcNumStrataRetainedExact,
                    other.CalcRankAtColumnIndex,
                    other.IterRetainedRanks,
                )
            else:
                return False

        def __hash__(self: "PolicyCoupler") -> int:
            """Hash object instance."""
            return hash(self._policy_spec)

        def __repr__(self: "PolicyCoupler") -> str:
            return f"""{
                self._policy_spec.GetAlgoIdentifier()
            }.{
                PolicyCoupler.__qualname__
            }(policy_spec={
                self._policy_spec
            !r})"""

        def __str__(self: "PolicyCoupler") -> str:
            return str(self._policy_spec)

        def GetEvalCtor(self: "PolicyCoupler") -> str:
            return f"""hstrat.{
                self._policy_spec.GetAlgoIdentifier()
            }.Policy(policy_spec={
                self._policy_spec.GetEvalCtor()
            })"""

        def GetSpec(self: "PolicyCoupler") -> policy_spec_t_:
            """Get policy's parameter specification."""
            return self._policy_spec

        def WithoutCalcRankAtColumnIndex(
            self: "PolicyCoupler",
        ) -> "PolicyCoupler":
            """Make a copy of this policy instance with CalcRankAtColumnIndex
            disabled.

            Useful to prevent optimization-out of strata rank number storage in
            a stratum ordered store backing a hereditary stratigraphic column.
            """
            type_ = PolicyCouplerFactory(
                policy_spec_t=policy_spec_t_,
                # enactment
                gen_drop_ranks_ftor_t=gen_drop_ranks_ftor_t,
                # invariants
                calc_mrca_uncertainty_abs_upper_bound_ftor_t=calc_mrca_uncertainty_abs_upper_bound_ftor_t,
                calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor_t=calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor_t,
                calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor_t=calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor_t,
                calc_mrca_uncertainty_rel_upper_bound_ftor_t=calc_mrca_uncertainty_rel_upper_bound_ftor_t,
                calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor_t=calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor_t,
                calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor_t=calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor_t,
                calc_num_strata_retained_upper_bound_ftor_t=calc_num_strata_retained_upper_bound_ftor_t,
                # scrying
                calc_mrca_uncertainty_abs_exact_ftor_t=calc_mrca_uncertainty_abs_exact_ftor_t,
                calc_mrca_uncertainty_rel_exact_ftor_t=calc_mrca_uncertainty_rel_exact_ftor_t,
                calc_num_strata_retained_exact_ftor_t=calc_num_strata_retained_exact_ftor_t,
                calc_rank_at_column_index_ftor_t=None,
                iter_retained_ranks_ftor_t=iter_retained_ranks_ftor_t,
            )

            # propagate any glossing over over implementation details
            type_.__module__ = PolicyCoupler.__module__
            type_.__name__ = PolicyCoupler.__name__
            type_.__qualname__ = PolicyCoupler.__qualname__

            return type_(
                policy_spec=self._policy_spec,
            )

    return PolicyCoupler
