#pragma once
#ifndef HSTRAT_AUXLIB_BINARY_SEARCH_HPP_INCLUDE
#define HSTRAT_AUXLIB_BINARY_SEARCH_HPP_INCLUDE

#include <cassert>
#include <cstddef>
#include <limits>

namespace hstrat_auxlib {

template<typename Pred>
std::size_t binary_search(
  Pred pred,
  std::size_t min,
  std::size_t max
) {

  while (min != max) {
    std::size_t mid = (max + min) / 2;
    if (pred(mid)) max = mid;
    else min = mid + 1;
  }

  assert(pred(min));

  return min;

}

template<typename Pred>
std::size_t binary_search(
  Pred pred,
  std::size_t max
) {
  return hstrat_auxlib::binary_search<Pred>(pred, 0, max);
}

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_BINARY_SEARCH_HPP_INCLUDE
