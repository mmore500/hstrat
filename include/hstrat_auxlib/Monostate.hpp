#pragma once
#ifndef HSTRAT_AUXLIB_MONOSTATE_HPP_INCLUDE
#define HSTRAT_AUXLIB_MONOSTATE_HPP_INCLUDE

namespace hstrat_auxlib {

struct Monostate {

  constexpr bool operator==(const Monostate& other) const { return true; }

};

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_MONOSTATE_HPP_INCLUDE
