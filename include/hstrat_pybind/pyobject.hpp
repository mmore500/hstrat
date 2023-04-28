#pragma once
#ifndef HSTRAT_PYBIND_PYOBJECT_HPP_INCLUDE
#define HSTRAT_PYBIND_PYOBJECT_HPP_INCLUDE

#include <string>

#include <pybind11/pybind11.h>

#include "../../third-party/fmt/include/fmt/format.h"

#include "deepcopy.hpp"

namespace py = pybind11;

namespace hstrat_pybind {

// override operator== to use __eq__, operator< to use __lt__
class pyobject {

  py::object object;

public:

  pyobject(){}

  pyobject(const py::object& obj) : object(obj) {}

  pyobject Clone() const { return {hstrat_pybind::deepcopy(object)}; }

  operator py::object() const { return object; }

  bool operator==(const pyobject& other) const {
    return object.equal(other.object);
  }

  bool operator<(const pyobject& other) const {
    try {
      return object < other.object;
    // py::type_error doesn't catch all TypeErrors
    } catch (...) { return false; }
  }

  std::string Repr() const {
    return object.attr("__repr__")().cast<std::string>();
  }

  std::string Str() const {
    return object.attr("__str__")().cast<std::string>();
  }

};

} // namespace hstrat_pybind

template <>
struct fmt::formatter<hstrat_pybind::pyobject> {
  template <typename ParseContext>
  constexpr auto parse(ParseContext& ctx) { return ctx.begin(); }

  template <typename FormatContext>
  auto format(const hstrat_pybind::pyobject& obj, FormatContext& ctx) {
    return fmt::format_to(ctx.out(), "{}", obj.Str());
  }
};

#endif // #ifndef HSTRAT_PYBIND_PYOBJECT_HPP_INCLUDE
