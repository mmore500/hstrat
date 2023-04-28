#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYABSUPPERBOUNDWORSTCASEFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYABSUPPERBOUNDWORSTCASEFTOR_HPP_INCLUDE

#include <algorithm>
#include <cassert>
#include <type_traits>

#include "../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace impl {

struct CalcMrcaUncertaintyAbsUpperBoundWorstCaseFtor {

  template<typename POLICY_SPEC>
  explicit CalcMrcaUncertaintyAbsUpperBoundWorstCaseFtor(
    const POLICY_SPEC&
  ) {}

  constexpr bool operator==(
    const CalcMrcaUncertaintyAbsUpperBoundWorstCaseFtor& other
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

    // rectify negative-indexed actual_rank_of_mrca
    if constexpr (std::is_signed_v<HSTRAT_RANK_T>) {
      if (actual_rank_of_mrca < 0) {
        assert(first_num_strata_deposited);
        assert(second_num_strata_deposited);
        const HSTRAT_RANK_T least_last_rank = std::min(
          first_num_strata_deposited - 1,
          second_num_strata_deposited - 1
        );
        actual_rank_of_mrca += least_last_rank;
      }
    }
    assert(actual_rank_of_mrca >= 0);

    const auto least_num_strata_deposited = std::min(
      first_num_strata_deposited,
      second_num_strata_deposited
    );

    if (actual_rank_of_mrca == least_num_strata_deposited - 1) {
      return 0;
    } else {
      // equivalent to std::max(least_num_strata_deposited - 2, 0);
      return std::max<decltype(least_num_strata_deposited)>(
        least_num_strata_deposited,
        2
      ) - 2;
    }

  }

};

} // namespace impl
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_IMPL_CALCMRCAUNCERTAINTYABSUPPERBOUNDWORSTCASEFTOR_HPP_INCLUDE
