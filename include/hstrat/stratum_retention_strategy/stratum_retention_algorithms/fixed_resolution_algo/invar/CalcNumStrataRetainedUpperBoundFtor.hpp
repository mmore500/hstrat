#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCNUMSTRATARETAINEDUPPERBOUNDFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCNUMSTRATARETAINEDUPPERBOUNDFTOR_HPP_INCLUDE

#include <algorithm>

#include "../../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct CalcNumStrataRetainedUpperBoundFtor {

  template<typename POLICY_SPEC>
  explicit CalcNumStrataRetainedUpperBoundFtor(const POLICY_SPEC&) {}

  constexpr bool operator==(
    const CalcNumStrataRetainedUpperBoundFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  HSTRAT_RANK_T operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T num_strata_deposited
  ) const {

    const HSTRAT_RANK_T resolution = (
      policy.GetSpec().GetFixedResolution()
    );
    // +2 due to 0'th and num_strata_deposited - 1'th ranks
    return std::min(
        num_strata_deposited / resolution + 2,
        num_strata_deposited
    );

  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCNUMSTRATARETAINEDUPPERBOUNDFTOR_HPP_INCLUDE
