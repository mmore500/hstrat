#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYABSUPPERBOUNDATPESSIMALRANKFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYABSUPPERBOUNDATPESSIMALRANKFTOR_HPP_INCLUDE

#include "../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace impl {

struct CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankFtor {

  template<typename POLICY_SPEC>
  explicit CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankFtor(
    const POLICY_SPEC&
  ) {}

  consteval bool operator==(
    const CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  HSTRAT_RANK_T operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ) const {
    return policy.CalcMrcaUncertaintyAbsUpperBound(
      first_num_strata_deposited,
      second_num_strata_deposited,
      policy.CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
        first_num_strata_deposited,
        second_num_strata_deposited
      )
    );
  }

  };

} // namespace impl
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYABSUPPERBOUNDATPESSIMALRANKFTOR_HPP_INCLUDE
