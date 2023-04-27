#pragma once
#ifndef HSTRAT_AUXLIB_TRIVIALLYCOPYABLE_HPP_INCLUDE
#define HSTRAT_AUXLIB_TRIVIALLYCOPYABLE_HPP_INCLUDE

#include <concepts>

namespace hstrat_auxlib {

template <typename T>
concept TriviallyCopyable = std::is_trivially_copyable_v<T>;

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_TRIVIALLYCOPYABLE_HPP_INCLUDE
