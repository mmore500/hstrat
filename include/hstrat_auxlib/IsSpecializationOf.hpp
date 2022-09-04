#pragma once
#ifndef HSTRAT_AUXLIB_ISSPECIALIZATIONOF_HPP_INCLUDE
#define HSTRAT_AUXLIB_ISSPECIALIZATIONOF_HPP_INCLUDE

#include "is_specialization_of.hpp"

namespace hstrat_auxlib {

template<class T, template<typename...> class Template>
concept IsSpecializationOf = is_specialization_of<Template, T>::value;

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_ISSPECIALIZATIONOF_HPP_INCLUDE
