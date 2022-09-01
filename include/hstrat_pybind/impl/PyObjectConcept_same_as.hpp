#pragma once
#ifndef HSTRAT_PYBIND_IMPL_PYOBJECTCONCEPT_SAME_AS_HPP_INCLUDE
#define HSTRAT_PYBIND_IMPL_PYOBJECTCONCEPT_SAME_AS_HPP_INCLUDE

#include <concepts>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace hstrat_pybind {

template<class T> concept PyObjectConcept = std::same_as<T, py::object>;

}

#endif // #ifndef HSTRAT_PYBIND_IMPL_PYOBJECTCONCEPT_SAME_AS_HPP_INCLUDE
