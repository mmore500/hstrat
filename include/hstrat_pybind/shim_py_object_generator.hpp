#pragma once
#ifndef HSTRAT_PYBIND_SHIM_PY_OBJECT_GENERATOR_HPP_INCLUDE
#define HSTRAT_PYBIND_SHIM_PY_OBJECT_GENERATOR_HPP_INCLUDE

#include <pybind11/pybind11.h>

#include "../../third-party/cppcoro/include/cppcoro/generator.hpp"

namespace py = pybind11;

namespace hstrat_pybind {

template<typename T>
cppcoro::generator<T> shim_py_object_generator(py::object object) {
  for (auto val : object) {
    auto res = val.template cast<T>();
    co_yield res;
  }
}

} // namespace hstrat_pybind

#endif // #ifndef HSTRAT_PYBIND_SHIM_PY_OBJECT_GENERATOR_HPP_INCLUDE
