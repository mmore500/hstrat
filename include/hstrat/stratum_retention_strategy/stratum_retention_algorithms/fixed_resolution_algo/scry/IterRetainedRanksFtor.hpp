#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_ITERRETAINEDRANKSFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_ITERRETAINEDRANKSFTOR_HPP_INCLUDE

#include <cassert>
#include <type_traits>

#include "../../../../../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../../../../../hstrat_auxlib/IsSpecializationOf.hpp"

#include "../../../../config/HSTRAT_RANK_T.hpp"

#include "../../detail/PolicyCoupler.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct IterRetainedRanksFtor {

  template<typename POLICY_SPEC>
  explicit IterRetainedRanksFtor(const POLICY_SPEC&) {}

  consteval bool operator==(const IterRetainedRanksFtor& other) const {
    return true;
  }

  /**
  * @warning: returned generator lifetime cannot exceed policy's
  * (returned generator holds a reference to policy)
  */
  template<typename POLICY>
  cppcoro::generator<const HSTRAT_RANK_T> operator()(
    const POLICY& policy,
    const HSTRAT_RANK_T num_strata_deposited
  ) const {
    return do_call<POLICY>(
      policy,
      num_strata_deposited
    );
  }

private:

  // delegated implementation enables operator() template deduction
  template<typename POLICY>
  cppcoro::generator<const HSTRAT_RANK_T> do_call(
    std::conditional_t<
      hstrat_auxlib::is_specialization_of<
        hstrat::detail::PolicyCoupler,
        POLICY
      >::value,
      const POLICY&, // specialization of PolicyCoupler
      POLICY   // i.e., PyObjectPolicyShim
    > policy,
    const HSTRAT_RANK_T num_strata_deposited
  ) const {

    const HSTRAT_RANK_T resolution = policy.GetSpec().GetFixedResolution();
    assert(resolution);

    for (
      HSTRAT_RANK_T rank = 0;
      rank < num_strata_deposited;
      rank += resolution
    ) {
      co_yield rank;
    }

    if (num_strata_deposited > 1) {
      const HSTRAT_RANK_T last_rank = num_strata_deposited - 1;
      if (last_rank % resolution) {
        co_yield last_rank;
      }
    }

  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_ITERRETAINEDRANKSFTOR_HPP_INCLUDE
