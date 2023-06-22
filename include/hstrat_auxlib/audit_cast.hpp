#pragma once
#ifndef HSTRAT_AUXLIB_AUDIT_CAST_HPP_INCLUDE
#define HSTRAT_AUXLIB_AUDIT_CAST_HPP_INCLUDE

#include "safe_cast.hpp"

// copied from https://github.com/mmore500/conduit/blob/master/include/uitsl/debug/
namespace hstrat_auxlib {

template<typename Dst, typename Src>
inline Dst audit_cast(const Src value) {
  #ifndef NDEBUG
    return hstrat_auxlib::safe_cast<Dst, Src>( value );
  #else
    return static_cast<Dst>( value );
  #endif
}

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_AUDIT_CAST_HPP_INCLUDE
