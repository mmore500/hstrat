#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYABSUPPERBOUNDFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYABSUPPERBOUNDFTOR_HPP_INCLUDE

#include <assert.h>

#include "../../impl/CalcMrcaUncertaintyAbsUpperBoundWorstCaseFtor.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct CalcMrcaUncertaintyAbsUpperBoundFtor {

  template<typename POLICY_SPEC>
  explicit CalcMrcaUncertaintyAbsUpperBoundFtor(const POLICY_SPEC&) {}

  consteval bool operator==(
    const CalcMrcaUncertaintyAbsUpperBoundFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  HSTRAT_RANK_T operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ) const {

    const HSTRAT_RANK_T resolution = policy.GetSpec().GetFixedResolution();
    assert(resolution >= 1);
    const HSTRAT_RANK_T res = resolution - 1;

    return std::min<HSTRAT_RANK_T>(
      res,
      hstrat::impl::CalcMrcaUncertaintyAbsUpperBoundWorstCaseFtor{policy}(
        policy,
        first_num_strata_deposited,
        second_num_strata_deposited,
        actual_rank_of_mrca
      )
    );

  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYABSUPPERBOUNDFTOR_HPP_INCLUDE
