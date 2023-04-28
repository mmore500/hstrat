#pragma once
#ifndef HSTRAT_AUXLIB_BINARY_SEARCH_HPP_INCLUDE
#define HSTRAT_AUXLIB_BINARY_SEARCH_HPP_INCLUDE

#include <cassert>
#include <cstddef>
#include <limits>

namespace hstrat_auxlib {

// returns max on failure
template<typename Pred>
std::size_t binary_search(
  Pred pred,
  std::size_t min,
  const std::size_t max  // exclusive
) {

  std::size_t max_ = max - 1;
  while (min != max_) {
    std::size_t mid = (max_ + min) / 2;
    if (pred(mid)) max_ = mid;
    else min = mid + 1;
  }

  if (!pred(min)) {
    return max;
  }

  return min;

}

template<typename Pred>
std::size_t binary_search(
  Pred pred,
  const std::size_t max // exclusive
) {
  return hstrat_auxlib::binary_search<Pred>(pred, 0, max);
}

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_BINARY_SEARCH_HPP_INCLUDE
