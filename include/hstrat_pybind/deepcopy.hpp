#pragma once
#ifndef HSTRAT_PYBIND_DEEPCOPY_HPP_INCLUDE
#define HSTRAT_PYBIND_DEEPCOPY_HPP_INCLUDE

#include "pybind11_or_stubs.hpp"

namespace py = pybind11;

namespace hstrat_pybind {

py::object deepcopy(py::object obj) {

  auto copylib = py::module::import("copy");
  return copylib.attr("deepcopy")(obj);

}

} // hamespace hstrat_pybind

#endif // #ifndef HSTRAT_PYBIND_DEEPCOPY_HPP_INCLUDE
