// cppimport
#include <pybind11/pybind11.h>

#include <hstrat_pybind/all_tu_declarations.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/PolicySpec.hpp>

namespace py = pybind11;
namespace algo = hstrat::fixed_resolution_algo;

using self_t = algo::PolicySpec;

PYBIND11_MODULE(_PolicySpecNative, m) {

  const auto class_ = py::class_<self_t>(m, "PolicySpecNative")
  .def(py::init<int>())
  .def("GetFixedResolution", &self_t::GetFixedResolution)
  .def("__eq__", &self_t::operator==)
  .def("__eq__", [](const py::object& self, const py::object& other){
    return other.attr("__eq__")(self).cast<bool>();
  })
  .def("__repr__", &self_t::Repr)
  .def("__str__", &self_t::Str)
  .def("GetEvalCtor", &self_t::GetEvalCtor)
  .def_static("GetAlgoIdentifier", &self_t::GetAlgoIdentifier)
  .def_static("GetAlgoTitle", &self_t::GetAlgoTitle);

  const auto import_module = py::module::import("importlib").attr(
    "import_module"
  );
  const auto PolicySpecABC_register = import_module(
    "...._detail", m.attr("__name__")
  ).attr("PolicySpecABC").attr("register");
  PolicySpecABC_register(class_);

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

cfg['extra_compile_args'] = ['-std=c++20', '-DFMT_HEADER_ONLY']
cfg['force_rebuild'] = True
cfg['include_dirs'] = [f'{root_dir}/include']

setup_pybind11(cfg)
%>
*/
