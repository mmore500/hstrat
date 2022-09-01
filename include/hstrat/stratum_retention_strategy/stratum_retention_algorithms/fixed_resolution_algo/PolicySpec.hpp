#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPEC_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPEC_HPP_INCLUDE

#include <format>
#include <string>

#include "../../../../../hstrat_pybind/PyObjectConcept.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

class PolicySpec {

  int fixed_resolution;

public:

  PolicySpec(
    const int fixed_resolution
  ) : fixed_resolution(fixed_resolution)
  { }

  PolicySpec(
    PyObjectConcept auto policy_spec
  ) : fixed_resolution(policy_spec.attr("GetFixedResolution")().cast<int>())
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

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPEC_HPP_INCLUDE
