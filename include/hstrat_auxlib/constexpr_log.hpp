#pragma once
#ifndef HSTRAT_AUXLIB_CONSTEXPR_LOG_HPP_INCLUDE
#define HSTRAT_AUXLIB_CONSTEXPR_LOG_HPP_INCLUDE

#include <cmath>
#include <type_traits>

#include "../../third-party/gcem/include/gcem.hpp"

namespace hstrat_auxlib {

constexpr double constexpr_log(const double arg) {

  if (std::is_constant_evaluated()) {
    return gcem::log(arg);
  } else {
    return std::log(arg);
  }

}

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_CONSTEXPR_LOG_HPP_INCLUDE
