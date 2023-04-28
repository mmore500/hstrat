#pragma once
#ifndef HSTRAT_AUXLIB_CONTAINER_HPP_INCLUDE
#define HSTRAT_AUXLIB_CONTAINER_HPP_INCLUDE

#include <concepts>
#include <iterator>

namespace hstrat_auxlib {

template <typename T>
concept Container = requires(T t) {
  { std::begin(t) } -> std::input_or_output_iterator;
  { std::end(t) } -> std::input_or_output_iterator;
  { t.size() } -> std::convertible_to<std::size_t>;
};

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_CONTAINER_HPP_INCLUDE
