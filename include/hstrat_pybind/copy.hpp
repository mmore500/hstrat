#pragma once
#ifndef HSTRAT_PYBIND_COPY_HPP_INCLUDE
#define HSTRAT_PYBIND_COPY_HPP_INCLUDE

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace hstrat_pybind {

py::object copy(py::object obj) {

  auto copylib = py::module::import("copy");
  return copylib.attr("copy")(obj);

}

} // hamespace hstrat_pybind

#endif // #ifndef HSTRAT_PYBIND_COPY_HPP_INCLUDE
