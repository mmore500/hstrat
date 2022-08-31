#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE

#include <format>
#include <string>

#include "get_policy_name.hpp"
#include "get_policy_title.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

template<int FIXED_RESOLUTION>
struct PolicySpecConsteval {

  static consteval int GetFixedResolution() { return FIXED_RESOLUTION; }

  static consteval std::string Repr() {
    return std::format(
      "{}(fixed_resolution={})",
      GetPolicyName(),
      GetFixedResolution()
    );
  }

  static consteval std::string Str() {
    return std::format(
      "{} (resolution: {})",
      GetPolicyTitle(),
      GetFixedResolution()
    );
  }

  static consteval std::string GetAlgoName() {
    return hstrat::fixed_resolution_algo::get_algo_name();
  }

  static consteval std::string GetAlgoTitle() {
    return hstrat::fixed_resolution_algo::get_algo_title();
  }

};


};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE
