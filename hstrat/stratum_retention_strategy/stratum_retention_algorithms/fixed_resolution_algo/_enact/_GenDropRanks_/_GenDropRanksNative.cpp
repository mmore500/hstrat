// cppimport
#include <pybind11/pybind11.h>

#include <hstrat_pybind/PyObjectIteratorShim.hpp>
#include <hstrat_pybind/PyObjectPolicyShim.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/enact/GenDropRanksFtor.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/PolicySpec.hpp>

namespace py = pybind11;
namespace algo = hstrat::fixed_resolution_algo;

using self_t = algo::GenDropRanksFtor<algo::PolicySpec>;

PYBIND11_MODULE(_GenDropRanksNative, m) {

  // ensure availability of algo::PolicySpec
  // see https://stackoverflow.com/questions/51833291/splitting-up-pybind11-modules-and-issues-with-automatic-type-conversion#comment113430868_51852400
  py::module::import("..._PolicySpec_.PolicySpecNative")

  py::class_<self_t>>(
    m,
    "GenDropRanksNative"
  )
  .def(py::init<const algo::PolicySpec&>())
  .def(py::init<py::object>)
  .def(
    "__call__",
    [](
      self_t& self,
      const algo::Policy& policy,
      const int num_stratum_depositions_completed,
      py::object retained_ranks
    ){
      return self(
        policy,
        num_stratum_depositions_completed,
        hstrat_auxlib::PyObjectIteratorShim<int>(retained_ranks),
      );
    }
  )
  .def(
    "__call__",
    [](
      self_t& self,
      py::object policy,
      const int num_stratum_depositions_completed,
      py::object retained_ranks
    ){
      return self(
        hstrat::auxlib::PyObjectPolicyShim(policy),
        num_stratum_depositions_completed,
        hstrat_auxlib::PyObjectIteratorShim<int>(retained_ranks),
      );
    }
  );
}

/*
<%
cfg['extra_compile_args'] = ['-std=c++20']
cfg['include_dirs'] = ['../../../../../../include']
setup_pybind11(cfg)
%>
*/
