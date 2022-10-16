#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_POLICYSPEC_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_POLICYSPEC_HPP_INCLUDE

#include <string>
#include <string_view>

#include "../../../../../third-party/fmt/include/fmt/core.h"

#include "../../../../hstrat_pybind/PyObjectConcept.hpp"

#include "get_algo_identifier.hpp"
#include "get_algo_title.hpp"

namespace hstrat {
namespace depth_proportional_resolution_algo {

class PolicySpec {

  int depth_proportional_resolution;

public:

  PolicySpec(
    const int depth_proportional_resolution
  ) : depth_proportional_resolution(depth_proportional_resolution)
  { }

  PolicySpec(
    hstrat_pybind::PyObjectConcept auto policy_spec
  ) : depth_proportional_resolution(
    policy_spec.attr("GetDepthProportionalResolution")().template cast<int>()
  )
  { }

  int GetDepthProportionalResolution() const {
    return depth_proportional_resolution;
  }

  bool operator==(const PolicySpec& other) const {
    return (
      depth_proportional_resolution
      == other.depth_proportional_resolution
    );
  }

  static constexpr std::string_view GetAlgoIdentifier() {
    return hstrat::depth_proportional_resolution_algo::get_algo_identifier();
  }

  static constexpr std::string_view GetAlgoTitle() {
    return hstrat::depth_proportional_resolution_algo::get_algo_title();
  }

  std::string Repr() const {
    return fmt::format(
      "{}::PolicySpec(depth_proportional_resolution={})",
      GetAlgoIdentifier(),
      GetDepthProportionalResolution()
    );
  }

  std::string Str() const {
    return fmt::format(
      "{} (resolution: {})",
      GetAlgoTitle(),
      GetDepthProportionalResolution()
    );
  }

  std::string GetEvalCtor() const {
    return fmt::format(
      "hstrat.{}.PolicySpec(depth_proportional_resolution={})",
      get_algo_identifier(),
      GetDepthProportionalResolution()
    );
  }

};

} // namespace depth_proportional_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_POLICYSPEC_HPP_INCLUDE
