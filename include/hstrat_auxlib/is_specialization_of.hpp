#pragma once
#ifndef HSTRAT_AUXLIB_IS_SPECILIAZATION_OF_HPP_INCLUDE
#define HSTRAT_AUXLIB_IS_SPECILIAZATION_OF_HPP_INCLUDE

#include <type_traits>

namespace hstrat_auxlib {

// adapted from https://stackoverflow.com/a/11251408/17332200
template<template<typename...> class Template, typename T>
struct is_specialization_of : std::false_type {};

template<template<typename...> class Template, typename... Args>
struct is_specialization_of<Template, Template<Args...>> : std::true_type {};

} // nsmespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_IS_SPECILIAZATION_OF_HPP_INCLUDE
