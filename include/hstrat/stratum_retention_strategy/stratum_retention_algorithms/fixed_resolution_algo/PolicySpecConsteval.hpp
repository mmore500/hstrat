#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE

#include <string>
#include <string_view>

#include "../../../../../third-party/fmt/include/fmt/core.h"

#include "get_algo_identifier.hpp"
#include "get_algo_title.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

template<int FIXED_RESOLUTION>
struct PolicySpecConsteval {

  static consteval int GetFixedResolution() { return FIXED_RESOLUTION; }

  static constexpr std::string_view GetAlgoIdentifier() {
    return hstrat::fixed_resolution_algo::get_algo_identifier();
  }

  static constexpr std::string_view GetAlgoTitle() {
    return hstrat::fixed_resolution_algo::get_algo_title();
  }

  constexpr bool operator==(
    const PolicySpecConsteval<FIXED_RESOLUTION>& other
  ) const {
    return true;
  }

  static std::string Repr() {
    return fmt::format(
      "{}(fixed_resolution={})",
      GetAlgoIdentifier(),
      GetFixedResolution()
    );
  }

  static std::string Str() {
    return fmt::format(
      "{} (resolution: {})",
      GetAlgoTitle(),
      GetFixedResolution()
    );
  }

  static std::string GetEvalCtor() {
    return fmt::format(
      "hstrat.{}.PolicySpec(fixed_resolution={})",
      get_algo_identifier(),
      GetFixedResolution()
    );
  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE
