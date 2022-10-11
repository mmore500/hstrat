#pragma once
#ifndef HSTRAT_PYBIND_PYOBJECT_HPP_INCLUDE
#define HSTRAT_PYBIND_PYOBJECT_HPP_INCLUDE

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace hstrat_pybind {

// override operator== to use __eq__
class pyobject {

  py::object object;

public:

  pyobject(){}

  pyobject(const py::object& obj) : object(obj) {}

  operator py::object() const { return object; }

  bool operator==(const pyobject& other) const {
    return object.equal(other.object);
  }

};

} // namespace hstrat_pybind

#endif // #ifndef HSTRAT_PYBIND_PYOBJECT_HPP_INCLUDE
