#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_IMPL_CALC_PROVIDED_UNCERTAINTY_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_IMPL_CALC_PROVIDED_UNCERTAINTY_HPP_INCLUDE

#include <assert.h>
#include <bit>

namespace hstrat {
namespace depth_proportional_resolution_algo {

template<typename POLICY>
int calc_provided_uncertainty(
  const POLICY& policy,
  const int num_stratum_depositions_completed
) {

  const auto& spec = policy.GetSpec();
  const auto resolution = spec.GetDepthProportionalResolution();

  const auto max_uncertainty = (
    num_stratum_depositions_completed / resolution
  );

  // round down to lower or equal power of 2
  assert(max_uncertainty > 0);
  return std::bit_floor(unsigned(max_uncertainty));

}

} // namespae depth_proportional_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_IMPL_CALC_PROVIDED_UNCERTAINTY_HPP_INCLUDE
