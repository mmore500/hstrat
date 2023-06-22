#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYRELUPPERBOUNDATPESSIMALRANKFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYRELUPPERBOUNDATPESSIMALRANKFTOR_HPP_INCLUDE

#include "../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace impl {

struct CalcMrcaUncertaintyRelUpperBoundAtPessimalRankFtor {

  template<typename POLICY_SPEC>
  explicit CalcMrcaUncertaintyRelUpperBoundAtPessimalRankFtor(
    const POLICY_SPEC&
  ) {}

  constexpr bool operator==(
    const CalcMrcaUncertaintyRelUpperBoundAtPessimalRankFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  double operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ) const {
    return policy.CalcMrcaUncertaintyRelUpperBound(
      first_num_strata_deposited,
      second_num_strata_deposited,
      policy.CalcMrcaUncertaintyRelUpperBoundPessimalRank(
        first_num_strata_deposited,
        second_num_strata_deposited
      )
    );
  }

  };

} // namespace impl
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYRELUPPERBOUNDATPESSIMALRANKFTOR_HPP_INCLUDE
