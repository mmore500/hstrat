#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_CALCMRCAUNCERTAINTYABSEXACTFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_CALCMRCAUNCERTAINTYABSEXACTFTOR_HPP_INCLUDE

#include <algorithm>
#include <cassert>

#include "../../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct CalcMrcaUncertaintyAbsExactFtor {

  template<typename POLICY_SPEC>
  explicit CalcMrcaUncertaintyAbsExactFtor(const POLICY_SPEC&) {}

  constexpr bool operator==(
    const CalcMrcaUncertaintyAbsExactFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  HSTRAT_RANK_T operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    HSTRAT_RANK_T actual_rank_of_mrca
  ) const {

    const HSTRAT_RANK_T resolution = policy.GetSpec().GetFixedResolution();

    const HSTRAT_RANK_T least_num_strata_deposited = std::min(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
    assert(least_num_strata_deposited);
    const HSTRAT_RANK_T least_last_rank = least_num_strata_deposited - 1;

    // rectify negative-indexed actual_rank_of_mrca
    if (actual_rank_of_mrca < 0) {
      actual_rank_of_mrca += least_last_rank;
      assert(actual_rank_of_mrca >= 0);
    }

    if (actual_rank_of_mrca == least_last_rank) return 0;
    // haven't added enough ranks to hit resolution
    else if (least_last_rank < resolution) {
      assert(least_last_rank);
      return least_last_rank - 1;
    }
    // mrca between last regularly-spaced rank and tail rank
    else if (actual_rank_of_mrca >= (
      least_last_rank - least_last_rank % resolution
    )) {
      assert(least_last_rank);
      return (least_last_rank - 1) % resolution;
    }
    // mrca between two regularly-spaced ranks
    else {
      assert(resolution);
      return resolution - 1;
    }

  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_CALCMRCAUNCERTAINTYABSEXACTFTOR_HPP_INCLUDE
