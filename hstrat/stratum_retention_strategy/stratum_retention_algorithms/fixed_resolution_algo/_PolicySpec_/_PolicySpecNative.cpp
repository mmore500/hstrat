// cppimport
#include <pybind11/pybind11.h>

#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/PolicySpec.hpp>

namespace py = pybind11;
namespace algo = hstrat::fixed_resolution_algo;

using self_t = algo::PolicySpec;

PYBIND11_MODULE(_PolicySpecNative, m) {

  py::class_<self_t>>(
    m,
    "PolicySpecNative"
  )
  .def(py::init<int>())
  .def("GetFixedResolution", &self_t::GetFixedResolution)
  .def("__repr__", &self_t::Repr)
  .def("__str__", &self_t::Str)
  .def_static("GetAlgoName", &self_t::GetAlgoName)
  .def_static("GetAlgoTitle", &self_t::GetAlgoTitle);

}

/*
<%
cfg['extra_compile_args'] = ['-std=c++20']
cfg['include_dirs'] = ['../../../../../include']
setup_pybind11(cfg)
%>
*/
