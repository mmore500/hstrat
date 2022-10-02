#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_CALCNUMSTRATARETAINEDEXACTFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_CALCNUMSTRATARETAINEDEXACTFTOR_HPP_INCLUDE

#include <assert.h>

#include "../../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct CalcNumStrataRetainedExactFtor {

  template<typename POLICY_SPEC>
  explicit CalcNumStrataRetainedExactFtor(const POLICY_SPEC&) {}

  consteval bool operator==(
    const CalcNumStrataRetainedExactFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  HSTRAT_RANK_T operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T num_strata_deposited
  ) const {

    if (num_strata_deposited == 0) return 0;

    const HSTRAT_RANK_T uncertainty = (
      policy.GetSpec().GetFixedResolution()
    );

    assert(num_strata_deposited);
    const HSTRAT_RANK_T newest_stratum_rank = num_strata_deposited - 1;
    // +1 for 0'th rank stratum
    const HSTRAT_RANK_T num_strata_at_uncertainty_intervals = (
      newest_stratum_rank / uncertainty + 1
    );
    const HSTRAT_RANK_T newest_stratum_distinct_from_uncertainty_intervals = (
      newest_stratum_rank % uncertainty != 0
    );
    return (
      num_strata_at_uncertainty_intervals
      + newest_stratum_distinct_from_uncertainty_intervals
    );

  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_CALCNUMSTRATARETAINEDEXACTFTOR_HPP_INCLUDE
