#pragma once
#ifndef HSTRAT_AUXLIB_HASLESSTHANOPERATOR_HPP_INCLUDE
#define HSTRAT_AUXLIB_HASLESSTHANOPERATOR_HPP_INCLUDE

#include <concepts>

namespace hstrat_auxlib {

template<typename T>
concept HasLessThanOperator = requires(T a, T b) {
    { a < b } -> std::convertible_to<bool>;
};

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_HASLESSTHANOPERATOR_HPP_INCLUDE
