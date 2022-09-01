#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_ITERRETAINEDRANKSFTOR_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_ITERRETAINEDRANKSFTOR_HPP_INCLUDE

namespace hstrat {
namespace fixed_resolution_algo {

struct IterRetainedRanksFtor {

  template<typename POLICY_SPEC>
  explicit IterRetainedRanksFtor(const POLICY_SPEC&) {}

  template<typename POLICY>
  void operator()(const POLICY& policy) const {

  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_SCRY_ITERRETAINEDRANKSFTOR_HPP_INCLUDE
