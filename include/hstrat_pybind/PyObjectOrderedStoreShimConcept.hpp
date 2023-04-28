#pragma once
#ifndef HSTRAT_PYBIND_PYOBJECTORDEREDSTORESHIMCONCEPT_HPP_INCLUDE
#define HSTRAT_PYBIND_PYOBJECTORDEREDSTORESHIMCONCEPT_HPP_INCLUDE

#if __has_include(<pybind11/pybind11.h>)
#include "impl/PyObjectOrderedStoreShimConcept_specialization_of.hpp"
#else
#include "impl/PyObjectOrderedStoreShimConcept_false.hpp"
#endif

#endif // #ifndef HSTRAT_PYBIND_PYOBJECTORDEREDSTORESHIMCONCEPT_HPP_INCLUDE
