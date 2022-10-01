#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYRELUPPERBOUNDPESSIMALRANKFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYRELUPPERBOUNDPESSIMALRANKFTOR_HPP_INCLUDE

#include <algorithm>
#include <assert.h>

#include "../../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct CalcMrcaUncertaintyRelUpperBoundPessimalRankFtor {

  template<typename POLICY_SPEC>
  CalcMrcaUncertaintyRelUpperBoundPessimalRankFtor(const POLICY_SPEC&) {}

  consteval bool operator==(
    const CalcMrcaUncertaintyRelUpperBoundPessimalRankFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  HSTRAT_RANK_T operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ) const {
    // eqivalent to
    // const HSTRAT_RANK_T least_last_rank = std::min(
    //   first_num_strata_deposited - 1,
    //   second_num_strata_deposited - 1,
    // );
    // return std::max(least_last_rank - 1, 0);

    const HSTRAT_RANK_T least_num_strata_deposited = std::min(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
    return std::max<HSTRAT_RANK_T>(
      least_num_strata_deposited,
      2
    ) - 2;
  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYRELUPPERBOUNDPESSIMALRANKFTOR_HPP_INCLUDE
