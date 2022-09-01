#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE

#include <string>
#include <string_view>

#include "../../../../../third-party/fmt/include/fmt/core.h"

#include "get_algo_name.hpp"
#include "get_algo_title.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

template<int FIXED_RESOLUTION>
struct PolicySpecConsteval {

  static consteval int GetFixedResolution() { return FIXED_RESOLUTION; }

  static std::string Repr() {
    return fmt::format(
      "{}(fixed_resolution={})",
      GetAlgoName(),
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

  static consteval std::string_view GetAlgoName() {
    return hstrat::fixed_resolution_algo::get_algo_name();
  }

  static consteval std::string_view GetAlgoTitle() {
    return hstrat::fixed_resolution_algo::get_algo_title();
  }

};

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICYSPECCONSTEVAL_HPP_INCLUDE
