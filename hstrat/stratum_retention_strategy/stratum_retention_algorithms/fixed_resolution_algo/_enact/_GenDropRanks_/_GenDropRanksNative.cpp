// cppimport
#include <iostream>

#include <pybind11/pybind11.h>

#include <hstrat_pybind/PyObjectPolicyShim.hpp>
#include <hstrat_pybind/shim_py_object_generator.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/enact/GenDropRanksFtor.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/PolicySpec.hpp>

namespace py = pybind11;
namespace algo = hstrat::fixed_resolution_algo;

using self_t = algo::GenDropRanksFtor;

PYBIND11_MODULE(_GenDropRanksNative, m) {

  // ensure availability of algo::PolicySpec
  // see https://stackoverflow.com/questions/51833291/splitting-up-pybind11-modules-and-issues-with-automatic-type-conversion#comment113430868_51852400
  py::module::import("cppimport.import_hook");
  auto importlib = py::module::import("importlib");
  importlib.attr("import_module")(
    "......._bindings",
    m.attr("__name__")
  );
  importlib.attr("import_module")(
    "...._PolicySpec_",
    m.attr("__name__")
  );

  py::class_<self_t>(
    m,
    "GenDropRanksNative"
  )
  .def(py::init<const algo::PolicySpec&>())
  .def(
    py::init([](py::object py_policy_spec) {
      auto policy_spec = algo::PolicySpec{py_policy_spec};
      return self_t{policy_spec};
    })
  )
  .def(
    "__call__",
    [](
      const self_t& self,
      py::object policy,
      const int num_stratum_depositions_completed,
      py::object retained_ranks
    ){
      return self(
        hstrat_pybind::PyObjectPolicyShim<algo::PolicySpec>(policy),
        num_stratum_depositions_completed,
        hstrat_pybind::shim_py_object_generator<const int>(retained_ranks)
      );
    }
  );
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

cfg['extra_compile_args'] = ['-std=c++2a', '-fconcepts','-fcoroutines', '-DFMT_HEADER_ONLY', '-g']
cfg['force_rebuild'] = True
cfg['include_dirs'] = [f'{root_dir}/include']

setup_pybind11(cfg)
%>
*/
