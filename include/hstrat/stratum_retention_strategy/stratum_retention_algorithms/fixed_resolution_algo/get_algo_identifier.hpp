#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_GET_ALGO_IDENTIFIER_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_GET_ALGO_IDENTIFIER_HPP_INCLUDE

#include <string_view>

namespace hstrat {
namespace fixed_resolution_algo {

constexpr std::string_view get_algo_identifier() {
  return "fixed_resolution_algo";
}

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_GET_ALGO_IDENTIFIER_HPP_INCLUDE
