#pragma once
#ifndef HSTRAT_AUXLIB_REPR_HPP_INCLUDE
#define HSTRAT_AUXLIB_REPR_HPP_INCLUDE

#include <string>
#include <string_view>
#include <type_traits>

#include "../../third-party/fmt/include/fmt/format.h"

namespace hstrat_auxlib {

template<typename T>
std::string repr(const T& obj) {
  if constexpr (std::is_convertible_v<T, std::string_view>) {
      const char quote = (obj.find('\'') == std::string::npos) ? '\'' : '"';
      return fmt::format("{}{}{}", quote, obj, quote);
  } else if constexpr (
    std::is_same_v<std::decay_t<T>, hstrat_pybind::pyobject>
  ) {
    return obj.Repr();
  } else return fmt::format("{}", obj);
}

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_REPR_HPP_INCLUDE
