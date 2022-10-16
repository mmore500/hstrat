#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_CALCRANKATCOLUMNINDEXFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_CALCRANKATCOLUMNINDEXFTOR_HPP_INCLUDE

#include <algorithm>
#include <cassert>

#include "../../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct CalcRankAtColumnIndexFtor {

  template<typename POLICY_SPEC>
  explicit CalcRankAtColumnIndexFtor(const POLICY_SPEC&) {}

  consteval bool operator==(
    const CalcRankAtColumnIndexFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  HSTRAT_RANK_T operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T index,
    const HSTRAT_RANK_T num_strata_deposited
  ) const {

    const auto resolution = policy.GetSpec().GetFixedResolution();

    // upper bound implementation gives the exact number of strata retained
    if (index == policy.CalcNumStrataRetainedExact(num_strata_deposited)) {
      // in-progress deposition case
      return num_strata_deposited;
    } else {
      assert(num_strata_deposited);
      return std::min(
        index * resolution,
        num_strata_deposited - 1
      );
    }

  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_CALCRANKATCOLUMNINDEXFTOR_HPP_INCLUDE
