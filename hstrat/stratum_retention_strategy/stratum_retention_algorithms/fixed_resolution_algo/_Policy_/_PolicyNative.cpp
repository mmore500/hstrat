// cppimport
#include <memory>

#include <pybind11/pybind11.h>

#include <hstrat/config/HSTRAT_RANK_T.hpp>
#include <hstrat_pybind/all_tu_declarations.hpp>
#include <hstrat_pybind/PyObjectPolicyShim.hpp>
#include <hstrat_pybind/shim_py_object_generator.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/Policy.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/PolicySpec.hpp>

namespace py = pybind11;
using namespace pybind11::literals; // to bring in the `_a` literal

namespace algo = hstrat::fixed_resolution_algo;

using self_t = algo::Policy<>;

PYBIND11_MODULE(_PolicyNative, m) {

  // ensure availability of algo::PolicySpec
  // see https://stackoverflow.com/questions/51833291/splitting-up-pybind11-modules-and-issues-with-automatic-type-conversion#comment113430868_51852400
  py::module::import("cppimport.import_hook");
  auto importlib = py::module::import("importlib");
  importlib.attr("import_module")(
    "......_bindings",
    m.attr("__name__")
  );
  importlib.attr("import_module")(
    "..._PolicySpec_",
    m.attr("__name__")
  );

  py::class_<self_t>(
    m,
    "PolicyNative"
  )
  .def(py::init<HSTRAT_RANK_T>())
  .def(py::init<const algo::PolicySpec&>())
  .def(
    py::init([](py::kwargs kwarg) {
      const auto py_policy_spec = kwarg["policy_spec"].template cast<py::object>();
      const auto policy_spec = algo::PolicySpec{py_policy_spec};
      // auto policy_spec = algo::PolicySpec{py_policy_spec};
      // not sure if this is necessary vs just returning self_t{policy_spec}
      return std::make_unique<self_t>(policy_spec);
    })
  )
  .def("__eq__", &self_t::operator==)
  .def("__eq__", [](const self_t&, py::object) { return false; })
  .def("__repr__", &self_t::Repr)
  .def("__str__", &self_t::Str)
  .def("GetSpec", &self_t::GetSpec)
  .def("HasCalcRankAtColumnIndex", [](const self_t&){
    return self_t::has_calc_rank_at_column_index();
  })
  .def("WithoutCalcRankAtColumnIndex", &self_t::WithoutCalcRankAtColumnIndex)
  // enact
  .def("GenDropRanks", [](
    const self_t& self,
    const HSTRAT_RANK_T num_stratum_depositions_completed,
    py::object retained_ranks
  ){
    return self.GenDropRanks(
      num_stratum_depositions_completed,
      hstrat_pybind::shim_py_object_generator<const HSTRAT_RANK_T>(retained_ranks)
    );
  }, py::keep_alive<0, 1>())
  // invar
  .def("CalcMrcaUncertaintyAbsUpperBound", [](
    const self_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ){
    return self.CalcMrcaUncertaintyAbsUpperBound(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    );
  })
  .def("CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank", [](
    const self_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ){
    return self.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
  })
  .def("CalcMrcaUncertaintyAbsUpperBoundPessimalRank", [](
    const self_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ){
    return self.CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
  })
  .def("CalcMrcaUncertaintyRelUpperBound", [](
    const self_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ){
    return self.CalcMrcaUncertaintyRelUpperBound(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    );
  })
  .def("CalcMrcaUncertaintyRelUpperBoundAtPessimalRank", [](
    const self_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ){
    return self.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
  })
  .def("CalcMrcaUncertaintyRelUpperBoundPessimalRank", [](
    const self_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ){
    return self.CalcMrcaUncertaintyRelUpperBoundPessimalRank(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
  })
  .def("CalcNumStrataRetainedUpperBound", [](
    const self_t& self,
    const HSTRAT_RANK_T num_strata_deposited
  ){
    return self.CalcNumStrataRetainedUpperBound(num_strata_deposited);
  })
  // scry
  .def("CalcMrcaUncertaintyAbsExact", [](
    const self_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ){
    return self.CalcMrcaUncertaintyAbsExact(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    );
  })
  .def("CalcMrcaUncertaintyRelExact", [](
    const self_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ){
    return self.CalcMrcaUncertaintyRelExact(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    );
  })
  .def("CalcNumStrataRetainedExact", [](
    const self_t& self,
    const HSTRAT_RANK_T num_strata_deposited
  ){
    return self.CalcNumStrataRetainedExact(num_strata_deposited);
  })
  .def("CalcRankAtColumnIndex", [](
    const self_t& self,
    const HSTRAT_RANK_T index,
    const HSTRAT_RANK_T num_strata_deposited

  ){
    return self.CalcRankAtColumnIndex(index, num_strata_deposited);
  })
  .def("IterRetainedRanks", [](
    const self_t& self,
    const HSTRAT_RANK_T num_strata_deposited
  ){
    return self.IterRetainedRanks(num_strata_deposited);
  }, py::keep_alive<0, 1>());

  using without_t = self_t::without_calc_rank_at_column_index_t;
  py::class_<without_t>(
    m,
    "PolicyNativeWithoutCalcRankAtColumnIndex"
  )
  .def(py::init<HSTRAT_RANK_T>())
  .def(py::init<const algo::PolicySpec&>())
  .def(
    py::init([](py::kwargs kwarg) {
      const auto py_policy_spec = kwarg["policy_spec"].template cast<py::object>();
      const auto policy_spec = algo::PolicySpec{py_policy_spec};
      // auto policy_spec = algo::PolicySpec{py_policy_spec};
      // not sure if this is necessary vs just returning without_t{policy_spec}
      return std::make_unique<without_t>(policy_spec);
    })
  )
  .def("__eq__", &without_t::operator==)
  .def("__eq__", [](const without_t&, py::object) { return false; })
  .def("__repr__", &without_t::Repr)
  .def("__str__", &without_t::Str)
  .def("GetSpec", &without_t::GetSpec)
  .def("HasCalcRankAtColumnIndex", [](const without_t&){
    return without_t::has_calc_rank_at_column_index();
  })
  .def("WithoutCalcRankAtColumnIndex", &without_t::WithoutCalcRankAtColumnIndex)
  // enact
  .def("GenDropRanks", [](
    const without_t& self,
    const HSTRAT_RANK_T num_stratum_depositions_completed,
    py::object retained_ranks
  ){
    return self.GenDropRanks(
      num_stratum_depositions_completed,
      hstrat_pybind::shim_py_object_generator<const HSTRAT_RANK_T>(retained_ranks)
    );
  }, py::keep_alive<0, 1>())
  // invar
  .def("CalcMrcaUncertaintyAbsUpperBound", [](
    const without_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ){
    return self.CalcMrcaUncertaintyAbsUpperBound(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    );
  })
  .def("CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank", [](
    const without_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ){
    return self.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
  })
  .def("CalcMrcaUncertaintyAbsUpperBoundPessimalRank", [](
    const without_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ){
    return self.CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
  })
  .def("CalcMrcaUncertaintyRelUpperBound", [](
    const without_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ){
    return self.CalcMrcaUncertaintyRelUpperBound(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    );
  })
  .def("CalcMrcaUncertaintyRelUpperBoundAtPessimalRank", [](
    const without_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ){
    return self.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
  })
  .def("CalcMrcaUncertaintyRelUpperBoundPessimalRank", [](
    const without_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ){
    return self.CalcMrcaUncertaintyRelUpperBoundPessimalRank(
      first_num_strata_deposited,
      second_num_strata_deposited
    );
  })
  .def("CalcNumStrataRetainedUpperBound", [](
    const without_t& self,
    const HSTRAT_RANK_T num_strata_deposited
  ){
    return self.CalcNumStrataRetainedUpperBound(num_strata_deposited);
  })
  // scry
  .def("CalcMrcaUncertaintyAbsExact", [](
    const without_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ){
    return self.CalcMrcaUncertaintyAbsExact(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    );
  })
  .def("CalcMrcaUncertaintyRelExact", [](
    const without_t& self,
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ){
    return self.CalcMrcaUncertaintyRelExact(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    );
  })
  .def("CalcNumStrataRetainedExact", [](
    const without_t& self,
    const HSTRAT_RANK_T num_strata_deposited
  ){
    return self.CalcNumStrataRetainedExact(num_strata_deposited);
  })
  .def_property_readonly(
    "CalcRankAtColumnIndex",
    [](const without_t& self){ return py::none(); }
  )
  .def("IterRetainedRanks", [](
    const without_t& self,
    const HSTRAT_RANK_T num_strata_deposited
  ){
    return self.IterRetainedRanks(num_strata_deposited);
  }, py::keep_alive<0, 1>());
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
