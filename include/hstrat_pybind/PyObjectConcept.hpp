#pragma once
#ifndef HSTRAT_PYBIND_PYOBJECTCONCEPT_HPP_INCLUDE
#define HSTRAT_PYBIND_PYOBJECTCONCEPT_HPP_INCLUDE

#if __has_include(<pybind11/pybind11.h>)
#include "impl/PyObjectConcept_same_as.hpp"
#else
#include "impl/PyObjectConcept_false.hpp"
#endif

#endif // #ifndef HSTRAT_PYBIND_PYOBJECTCONCEPT_HPP_INCLUDE
