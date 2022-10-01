#pragma once
#ifndef HSTRAT_AUXLIB_AUDIT_COMPARE_HPP_INCLUDE
#define HSTRAT_AUXLIB_AUDIT_COMPARE_HPP_INCLUDE

#include <limits>
#include <type_traits>

#include "audit_cast.hpp"

// copied from https://github.com/mmore500/conduit/blob/master/include/uitsl/debug/
namespace hstrat_auxlib {

template <typename I, typename J>
inline bool audit_greater(const I x, const J y) {

  if constexpr (
    std::numeric_limits<I>::is_signed != std::numeric_limits<J>::is_signed
  ) {
    return hstrat_auxlib::audit_cast<typename std::make_signed<I>::type>( x )
      > hstrat_auxlib::audit_cast<typename std::make_signed<J>::type>( y )
    ;
  } else return x > y;

}

template <typename I, typename J>
inline bool audit_less(const I x, const J y) {

  if constexpr (
    std::numeric_limits<I>::is_signed != std::numeric_limits<J>::is_signed
  ) {
    return hstrat_auxlib::audit_cast<typename std::make_signed<I>::type>( x )
      < hstrat_auxlib::audit_cast<typename std::make_signed<J>::type>( y )
    ;
  } else return x < y;

}

template <typename I, typename J>
inline bool audit_leq(const I x, const J y) {

  if constexpr (
    std::numeric_limits<I>::is_signed != std::numeric_limits<J>::is_signed
  ) {
    return hstrat_auxlib::audit_cast<typename std::make_signed<I>::type>( x )
      <= hstrat_auxlib::audit_cast<typename std::make_signed<J>::type>( y )
    ;
  } else return x <= y;

}

template <typename I, typename J>
inline bool audit_geq(const I x, const J y) {

  if constexpr (
    std::numeric_limits<I>::is_signed != std::numeric_limits<J>::is_signed
  ) {
    return hstrat_auxlib::audit_cast<typename std::make_signed<I>::type>( x )
      >= hstrat_auxlib::audit_cast<typename std::make_signed<J>::type>( y )
    ;
  } else return x >= y;

}

template <typename I, typename J>
inline bool audit_equal(const I x, const J y) {

  if constexpr (
    std::numeric_limits<I>::is_signed != std::numeric_limits<J>::is_signed
  ) {
    return hstrat_auxlib::audit_cast<typename std::make_signed<I>::type>( x )
      == hstrat_auxlib::audit_cast<typename std::make_signed<J>::type>( y )
    ;
  } else return x == y;

}

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_AUDIT_COMPARE_HPP_INCLUDE
