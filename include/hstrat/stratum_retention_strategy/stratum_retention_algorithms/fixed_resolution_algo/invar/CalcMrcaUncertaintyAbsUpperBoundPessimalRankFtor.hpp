#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYABSUPPERBOUNDPESSIMALRANKFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYABSUPPERBOUNDPESSIMALRANKFTOR_HPP_INCLUDE

#include "../../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct CalcMrcaUncertaintyAbsUpperBoundPessimalRankFtor {

  template<typename POLICY_SPEC>
  CalcMrcaUncertaintyAbsUpperBoundPessimalRankFtor(const POLICY_SPEC&) {}

  constexpr bool operator==(
    const CalcMrcaUncertaintyAbsUpperBoundPessimalRankFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  HSTRAT_RANK_T operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ) const {
    return 0;
  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYABSUPPERBOUNDPESSIMALRANKFTOR_HPP_INCLUDE
