#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYRELUPPERBOUNDWORSTCASEFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYRELUPPERBOUNDWORSTCASEFTOR_HPP_INCLUDE

#include <algorithm>
#include <cassert>
#include <type_traits>

#include "../../../config/HSTRAT_RANK_T.hpp"

#include "CalcMrcaUncertaintyAbsUpperBoundWorstCaseFtor.hpp"

namespace hstrat {
namespace impl {

struct CalcMrcaUncertaintyRelUpperBoundWorstCaseFtor {

  template<typename POLICY_SPEC>
  explicit CalcMrcaUncertaintyRelUpperBoundWorstCaseFtor(
    const POLICY_SPEC&
  ) {}

  constexpr bool operator==(
    const CalcMrcaUncertaintyRelUpperBoundWorstCaseFtor& other
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

    if (
      first_num_strata_deposited == 0
      || second_num_strata_deposited == 0
    ) return 0.0;

    const HSTRAT_RANK_T least_last_rank = std::min(
      first_num_strata_deposited - 1,
      second_num_strata_deposited - 1
    );

    // rectify negative-indexed actual_rank_of_mrca
    if constexpr (std::is_signed_v<HSTRAT_RANK_T>) {
      if (actual_rank_of_mrca < 0) {
        assert(first_num_strata_deposited);
        assert(second_num_strata_deposited);
        actual_rank_of_mrca += least_last_rank;
      }
    }
    assert(actual_rank_of_mrca >= 0);

    // conservatively normalize by smallest ranks since mrca
    assert(least_last_rank >= actual_rank_of_mrca);
    const HSTRAT_RANK_T min_ranks_since_mrca = (
      least_last_rank - actual_rank_of_mrca
    );
    const HSTRAT_RANK_T worst_abs_uncertainty = (
      CalcMrcaUncertaintyAbsUpperBoundWorstCaseFtor{policy}(
        policy,
        first_num_strata_deposited,
        second_num_strata_deposited,
        actual_rank_of_mrca
      )
    );

    if (min_ranks_since_mrca == 0) return 0.0;
    else {
      return static_cast<double>(worst_abs_uncertainty) / min_ranks_since_mrca;
    }

  }

};

} // namespace impl
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYRELUPPERBOUNDWORSTCASEFTOR_HPP_INCLUDE
