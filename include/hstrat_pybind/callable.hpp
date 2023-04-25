#pragma once
#ifndef HSTRAT_PYBIND_CALLABLE_HPP_INCLUDE
#define HSTRAT_PYBIND_CALLABLE_HPP_INCLUDE

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace hstrat_pybind {

bool callable(py::object obj) {

  auto copylib = py::module::import("builtins");
  return copylib.attr("callable")(obj).cast<bool>();

}

} // hamespace hstrat_pybind

#endif // #ifndef HSTRAT_PYBIND_CALLABLE_HPP_INCLUDE
