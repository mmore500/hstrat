#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYRELUPPERBOUNDFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYRELUPPERBOUNDFTOR_HPP_INCLUDE

#include <algorithm>
#include <cassert>

#include "../../../../config/HSTRAT_RANK_T.hpp"

#include "../../impl/CalcMrcaUncertaintyRelUpperBoundWorstCaseFtor.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct CalcMrcaUncertaintyRelUpperBoundFtor {

  template<typename POLICY_SPEC>
  explicit CalcMrcaUncertaintyRelUpperBoundFtor(const POLICY_SPEC&) {}

  constexpr bool operator==(
    const CalcMrcaUncertaintyRelUpperBoundFtor& other
  ) const {
    return true;
  }

  template<typename POLICY>
  double operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    HSTRAT_RANK_T actual_rank_of_mrca
  ) const {

    const HSTRAT_RANK_T first_last_rank = first_num_strata_deposited - 1;
    const HSTRAT_RANK_T second_last_rank = second_num_strata_deposited - 1;

    // rectify negative-indexed actual_rank_of_mrca
    if (actual_rank_of_mrca < 0) {
      assert(first_num_strata_deposited);
      assert(second_num_strata_deposited);
      const HSTRAT_RANK_T least_last_rank = std::min(
        first_last_rank,
        second_last_rank
      );
      actual_rank_of_mrca += least_last_rank;
      assert(actual_rank_of_mrca >= 0);
    }

    if (
      first_num_strata_deposited <= 2
      || second_num_strata_deposited <= 2
      || actual_rank_of_mrca == first_last_rank
      || actual_rank_of_mrca == second_last_rank
    ) return 0.0;

    const HSTRAT_RANK_T abs_upper_bound = (
      policy.CalcMrcaUncertaintyAbsUpperBound(
        first_num_strata_deposited,
        second_num_strata_deposited,
        actual_rank_of_mrca
      )
    );

    const HSTRAT_RANK_T least_last_rank = std::min(
      first_last_rank,
      second_last_rank
    );
    assert(actual_rank_of_mrca <= least_last_rank);
    const HSTRAT_RANK_T least_recency = least_last_rank - actual_rank_of_mrca;

    // worst-case recency is 1
    assert(least_recency >= 1);
    double res = (
      static_cast<double>(abs_upper_bound)
      / least_recency
    );

    // tighten to worst-possible case given number of strata deposited
    return std::min(
        res,
        hstrat::impl::CalcMrcaUncertaintyRelUpperBoundWorstCaseFtor{policy}(
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

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_INVAR_CALCMRCAUNCERTAINTYRELUPPERBOUNDFTOR_HPP_INCLUDE
