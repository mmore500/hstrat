#pragma once
#ifndef HSTRAT_PYBIND_ITER_HPP_INCLUDE
#define HSTRAT_PYBIND_ITER_HPP_INCLUDE

#include <utility>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace hstrat_pybind {

py::object iter(auto&&... args) {
  auto builtins = py::module::import("builtins");
  return builtins.attr("iter")(std::forward<decltype(args)>(args)...);
}

} // hamespace hstrat_pybind

#endif // #ifndef HSTRAT_PYBIND_ITER_HPP_INCLUDE
