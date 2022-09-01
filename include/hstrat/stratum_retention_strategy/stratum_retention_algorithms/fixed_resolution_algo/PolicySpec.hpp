#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPEC_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPEC_HPP_INCLUDE

#include <string>
#include <string_view>

#include "../../../../../third-party/fmt/include/fmt/core.h"

#include "../../../../hstrat_pybind/PyObjectConcept.hpp"

#include "get_algo_name.hpp"
#include "get_algo_title.hpp"

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
    hstrat_pybind::PyObjectConcept auto policy_spec
  ) : fixed_resolution(
    policy_spec.attr("GetFixedResolution")().template cast<int>()
  )
  { }

  int GetFixedResolution() const { return fixed_resolution; }

  std::string Repr() const {
    return fmt::format(
      "{}(fixed_resolution={})",
      GetAlgoName(),
      GetFixedResolution()
    );
  }

  std::string Str() const {
    return fmt::format(
      "{} (resolution: {})",
      GetAlgoTitle(),
      GetFixedResolution()
    );
  }

  static consteval std::string_view GetAlgoName() {
    return hstrat::fixed_resolution_algo::get_algo_name();
  }

  static consteval std::string_view GetAlgoTitle() {
    return hstrat::fixed_resolution_algo::get_algo_title();
  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPEC_HPP_INCLUDE
