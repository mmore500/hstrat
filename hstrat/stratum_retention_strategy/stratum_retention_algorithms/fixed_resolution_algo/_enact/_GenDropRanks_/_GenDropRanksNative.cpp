// cppimport
#include <pybind11/pybind11.h>

#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/enact/GenDropRanksFtor.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/PolicySpecDynamic.hpp>

namespace py = pybind11;
namespace algo = hstrat::fixed_resolution_algo;

using instance_t = algo::GenDropRanksFtor<algo::PolicySpecDynamic>;

PYBIND11_MODULE(GenDropRanksNative, m) {
  py::class_<instance_t>>(
    m,
    "GenDropRanksNative"
  )
  .def(py::init<const algo::PolicySpecDynamic&>())
  .def(
    "__call__",
    [](instance_t& self, const algo::PolicySpecDynamic& spec){
      return this(spec);
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
