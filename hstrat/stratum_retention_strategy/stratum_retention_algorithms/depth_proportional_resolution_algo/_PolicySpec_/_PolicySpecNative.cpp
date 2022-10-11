// cppimport
#include <pybind11/pybind11.h>

#include <hstrat_pybind/all_tu_declarations.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/depth_proportional_resolution_algo/PolicySpec.hpp>

namespace py = pybind11;
namespace algo = hstrat::depth_proportional_resolution_algo;

using self_t = algo::PolicySpec;

PYBIND11_MODULE(_PolicySpecNative, m) {

  py::class_<self_t>(m, "PolicySpecNative")
  .def(py::init<int>())
  .def(
    "GetDepthProportionalResolution", &self_t::GetDepthProportionalResolution
  )
  .def("__eq__", &self_t::operator==)
  .def("__repr__", &self_t::Repr)
  .def("__str__", &self_t::Str)
  .def_static("GetAlgoIdentifier", &self_t::GetAlgoIdentifier)
  .def_static("GetAlgoTitle", &self_t::GetAlgoTitle);

}

/*
<%
import os
import subprocess

os.environ["CC"] = os.environ.get(
  "CC",
  os.environ.get("CXX", "g++"),
)
root_dir = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')

cfg['extra_compile_args'] = ['-std=c++2a', '-fconcepts','-fcoroutines', '-DFMT_HEADER_ONLY']
cfg['force_rebuild'] = True
cfg['include_dirs'] = [f'{root_dir}/include']

setup_pybind11(cfg)
%>
*/
