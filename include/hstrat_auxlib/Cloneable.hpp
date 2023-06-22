#pragma once
#ifndef HSTRAT_AUXLIB_CLONEABLE_HPP_INCLUDE
#define HSTRAT_AUXLIB_CLONEABLE_HPP_INCLUDE

#include <concepts>

namespace hstrat_auxlib {

template <typename T>
concept Cloneable = requires(T obj) {
  { obj.Clone() } -> std::convertible_to<T>;
};

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_CLONEABLE_HPP_INCLUDE
