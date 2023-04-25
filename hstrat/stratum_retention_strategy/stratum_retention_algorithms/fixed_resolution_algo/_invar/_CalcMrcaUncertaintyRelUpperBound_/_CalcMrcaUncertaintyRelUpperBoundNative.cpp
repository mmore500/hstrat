// cppimport
#include <memory>

#include <pybind11/pybind11.h>

#include <hstrat/config/HSTRAT_RANK_T.hpp>
#include <hstrat_pybind/all_tu_declarations.hpp>
#include <hstrat_pybind/PyObjectPolicyShim.hpp>
#include <hstrat_pybind/shim_py_object_generator.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/invar/CalcMrcaUncertaintyRelUpperBoundFtor.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/PolicySpec.hpp>

namespace py = pybind11;
namespace algo = hstrat::fixed_resolution_algo;

using self_t = algo::CalcMrcaUncertaintyRelUpperBoundFtor;

PYBIND11_MODULE(_CalcMrcaUncertaintyRelUpperBoundNative, m) {

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
    "CalcMrcaUncertaintyRelUpperBoundNative"
  )
  .def(py::init<const algo::PolicySpec&>())
  .def(
    py::init([](py::object py_policy_spec) {
      auto policy_spec = algo::PolicySpec{py_policy_spec};
      // not sure if this is necessary vs just returning self_t{policy_spec}
      return std::make_unique<self_t>(policy_spec);
    })
  )
  .def("__eq__", &self_t::operator==)
  .def(
    "__call__",
    [](
      const self_t& self,
      py::object policy,
      const HSTRAT_RANK_T first_num_strata_deposited,
      const HSTRAT_RANK_T second_num_strata_deposited,
      const HSTRAT_RANK_T actual_rank_of_mrca
    ){
      return self(
        hstrat_pybind::PyObjectPolicyShim<algo::PolicySpec>(policy),
        first_num_strata_deposited,
        second_num_strata_deposited,
        actual_rank_of_mrca
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

cfg['extra_compile_args'] = ['-std=c++2a', '-fconcepts','-fcoroutines', '-DFMT_HEADER_ONLY']
cfg['force_rebuild'] = True
cfg['include_dirs'] = [f'{root_dir}/include']

setup_pybind11(cfg)
%>
*/
