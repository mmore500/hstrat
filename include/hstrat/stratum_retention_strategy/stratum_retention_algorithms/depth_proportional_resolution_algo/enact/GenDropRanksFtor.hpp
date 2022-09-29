#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_ENACT_GENDROPRANKSFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_ENACT_GENDROPRANKSFTOR_HPP_INCLUDE

#include <assert.h>
#include <type_traits>
#include <utility>

#include "../../../../../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../../../../../hstrat_auxlib/IsSpecializationOf.hpp"

#include "../../detail/PolicyCoupler.hpp"

#include "../impl/calc_provided_uncertainty.hpp"

namespace hstrat {
namespace depth_proportional_resolution_algo {

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
    const auto resolution = spec.GetDepthProportionalResolution();

    // until sufficient strata have been deposited to reach target resolution
    // don't remove any strata
    if (num_stratum_depositions_completed <= resolution) co_return;

    // newest stratum is in-progress deposition
    // that will occupy rank num_stratum_depositions_completed
    const auto second_newest_stratum_rank = (
      num_stratum_depositions_completed - 1
    );

    // +1's because of in-progress deposition
    // _calc_provided_uncertainty is from super class
    const auto cur_provided_uncertainty = calc_provided_uncertainty<POLICY>(
      policy,
      num_stratum_depositions_completed + 1
    );
    const auto prev_provided_uncertainty = calc_provided_uncertainty<POLICY>(
      policy,
      num_stratum_depositions_completed + 1 - 1
    );
    if (cur_provided_uncertainty != prev_provided_uncertainty) {
      // we just passed the threshold where the spacing between retained
      // strata could be doubled without violating our resolution guarantee
      // clean up no-longer-needed strata that bisect
      // cur_provided_uncertainty intervals
      assert(prev_provided_uncertainty * 2 == cur_provided_uncertainty);
      for (
        auto v = prev_provided_uncertainty;
        v < second_newest_stratum_rank;
        v += cur_provided_uncertainty
      ) co_yield v;
    }

    // check that optimization taking advantage that
    // cur_provided_uncertainty is power of 2 works properly
    assert(
      second_newest_stratum_rank & (cur_provided_uncertainty - 1)
      == second_newest_stratum_rank % cur_provided_uncertainty
    );
    if (second_newest_stratum_rank & (cur_provided_uncertainty - 1)) {
      // we always keep the newest stratum
      // but unless the now-second-newest stratum is needed as a waypoint
      // of the cur_provided_uncertainty intervals, get rid of it
      co_yield second_newest_stratum_rank;
    }

  }

};

} // namespace depth_proportional_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_ENACT_GENDROPRANKSFTOR_HPP_INCLUDE
