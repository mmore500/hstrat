#pragma once
#ifndef HSTRAT_CONFIG_PICK_DIFFERENTIA_HPP_INCLUDE
#define HSTRAT_CONFIG_PICK_DIFFERENTIA_HPP_INCLUDE

#include <algorithm>
#include <climits>
#include <functional>
#include <random>
#include <type_traits>
#include <vector>

#include "HSTRAT_RANK_T.hpp"


namespace hstrat {

// end users can create template specialization to override
template<typename DIFFERENTIA_T>
DIFFERENTIA_T pick_differentia(const HSTRAT_RANK_T deposition_rank) {

  // does not invoke ub
  // gcc: https://godbolt.org/z/czrY5orT4
  // clang: https://godbolt.org/z/rbhdqbPxh

  // adapted from https://stackoverflow.com/a/28490097/17332200
  using random_bytes_engine_t = std::independent_bits_engine<
    std::default_random_engine,
    CHAR_BIT,
    unsigned char
  >;
  thread_local random_bytes_engine_t rbe;

  DIFFERENTIA_T res;
  const auto res_begin = reinterpret_cast<unsigned char*>(&res);
  const auto res_end = res_begin + sizeof(res);
  std::generate(
    res_begin,
    res_end,
    std::ref(rbe)
  );

  if constexpr (std::is_same_v<DIFFERENTIA_T, bool>) {
    // normalize to {0,1} bool range
    // also, ensures even true/false distribution
    reinterpret_cast<unsigned char&>(res) %= 2;
  }

  return res;

}

} // namespace hstrat

#endif // #ifndef HSTRAT_CONFIG_PICK_DIFFERENTIA_HPP_INCLUDE
