#pragma once
#ifndef HSTRAT_AUXLIB_MONOSTATE_HPP_INCLUDE
#define HSTRAT_AUXLIB_MONOSTATE_HPP_INCLUDE

#include "../../third-party/fmt/include/fmt/format.h"

namespace hstrat_auxlib {

struct Monostate {

  constexpr bool operator==(const Monostate& other) const { return true; }

  constexpr bool operator<(const Monostate&) const { return false; }

};

} // namespace hstrat_auxlib

template <>
struct fmt::formatter<hstrat_auxlib::Monostate> {
  template <typename ParseContext>
  constexpr auto parse(ParseContext& ctx) { return ctx.begin(); }

  template <typename FormatContext>
  auto format(const hstrat_auxlib::Monostate& obj, FormatContext& ctx) {
    return fmt::format_to(ctx.out(), "{}", "None");
  }
};

#endif // #ifndef HSTRAT_AUXLIB_MONOSTATE_HPP_INCLUDE
