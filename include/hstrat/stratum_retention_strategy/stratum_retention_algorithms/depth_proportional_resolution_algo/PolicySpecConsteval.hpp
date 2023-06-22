#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE

#include <string>
#include <string_view>

#include "../../../../../third-party/fmt/include/fmt/core.h"

#include "get_algo_identifier.hpp"
#include "get_algo_title.hpp"

namespace hstrat {
namespace depth_proportional_resolution_algo {

template<int DEPTH_PROPORTIONAL_RESOLUTION>
struct PolicySpecConsteval {

  static consteval int GetDepthProportionalResolution() {
    return DEPTH_PROPORTIONAL_RESOLUTION;
  }

  constexpr bool operator==(
    const PolicySpecConsteval<DEPTH_PROPORTIONAL_RESOLUTION>& other
  ) const {
    return true;
  }

  static constexpr std::string_view GetAlgoIdentifier() {
    return hstrat::depth_proportional_resolution_algo::get_algo_identifier();
  }

  static constexpr std::string_view GetAlgoTitle() {
    return hstrat::depth_proportional_resolution_algo::get_algo_title();
  }

  static std::string Repr() {
    return fmt::format(
      "{}::PolicySpecConsteval(depth_proportional_resolution={})",
      GetAlgoIdentifier(),
      GetDepthProportionalResolution()
    );
  }

  static std::string Str() {
    return fmt::format(
      "{} (resolution: {})",
      GetAlgoTitle(),
      GetDepthProportionalResolution()
    );
  }

  static std::string GetEvalCtor() {
    return fmt::format(
      "hstrat.{}.PolicySpec(depth_proportional_resolution={})",
      get_algo_identifier(),
      GetDepthProportionalResolution()
    );
  }

};

} // namespace depth_proportional_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DEPTH_PROPORTIONAL_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE
