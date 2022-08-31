#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECDYNAMIC_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECDYNAMIC_HPP_INCLUDE

#include <format>
#include <string>

namespace hstrat {
namespace fixed_resolution_algo {

class PolicySpecDynamic {

  int fixed_resolution;

public:

  PolicySpecDynamic(
    const int fixed_resolution
  ) : fixed_resolution(fixed_resolution)
  { }

  int GetFixedResolution() const { return fixed_resolution; }

  std::string Repr() const {
    return std::format(
      "{}(fixed_resolution={})",
      GetPolicyName(),
      GetFixedResolution()
    );
  }

  std::string Str() const {
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

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECDYNAMIC_HPP_INCLUDE
