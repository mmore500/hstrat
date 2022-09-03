#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_ENACT_GENDROPRANKSFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_ENACT_GENDROPRANKSFTOR_HPP_INCLUDE

#include <type_traits>
#include <utility>

#include "../../../../../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../../../../../hstrat_auxlib/IsSpecializationOf.hpp"

#include "../../detail/PolicyCoupler.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

struct GenDropRanksFtor {

  template<typename POLICY_SPEC>
  explicit GenDropRanksFtor(const POLICY_SPEC&) {}

  /**
  * @warning: returned generator lifetime cannot exceed policy's
  * (returned generator holds a reference to policy)
  */
  template<typename POLICY>
  cppcoro::generator<const int> operator()(
    const POLICY& policy,
    const int num_stratum_depositions_completed,
    cppcoro::generator<const int> retained_ranks={}
  ) const {
    return do_call<POLICY>(
      policy,
      num_stratum_depositions_completed,
      std::move(retained_ranks)
    );
  }

private:

  // delegated implementation enables operator() template deduction
  template<typename POLICY>
  cppcoro::generator<const int> do_call(
    std::conditional<
      hstrat_auxlib::is_specialization_of<
        hstrat::detail::PolicyCoupler,
        POLICY
      >::value,
      const POLICY&, // specialization of PolicyCoupler
      POLICY   // i.e., PyObjectPolicyShim
    >::type policy,
    const int num_stratum_depositions_completed,
    cppcoro::generator<const int> retained_ranks={}
  ) const {

    const auto& spec = policy.GetSpec();
    const auto second_newest_stratum_rank = (
      num_stratum_depositions_completed - 1
    );

    if (
        num_stratum_depositions_completed > 1
        && second_newest_stratum_rank % spec.GetFixedResolution()
    ) {
      co_yield second_newest_stratum_rank;
    }

  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_ENACT_GENDROPRANKSFTOR_HPP_INCLUDE
