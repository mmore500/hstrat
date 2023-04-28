#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_IMPL_CALC_PROVIDED_UNCERTAINTY_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_IMPL_CALC_PROVIDED_UNCERTAINTY_HPP_INCLUDE

#include <bit>
#include <cassert>
#include <type_traits>

#include "../../../../../hstrat_auxlib/audit_cast.hpp"

#include "../../../../config/HSTRAT_RANK_T.hpp"

namespace hstrat {
namespace depth_proportional_resolution_algo {

template<typename POLICY>
HSTRAT_RANK_T calc_provided_uncertainty(
  const POLICY& policy,
  const HSTRAT_RANK_T num_stratum_depositions_completed
) {

  const auto& spec = policy.GetSpec();
  const auto resolution = spec.GetDepthProportionalResolution();

  const auto max_uncertainty = (
    num_stratum_depositions_completed / resolution
  );

  // round down to lower or equal power of 2
  assert(max_uncertainty > 0);
  if constexpr (std::is_signed_v<decltype(max_uncertainty)>) {
    using as_unsigned_t = std::make_unsigned_t<decltype(max_uncertainty)>;
    const auto as_unsigned = hstrat_auxlib::audit_cast<
      as_unsigned_t
    >(max_uncertainty);
    return std::bit_floor(as_unsigned);
  } else return std::bit_floor(max_uncertainty);

}

} // namespae depth_proportional_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_IMPL_CALC_PROVIDED_UNCERTAINTY_HPP_INCLUDE
