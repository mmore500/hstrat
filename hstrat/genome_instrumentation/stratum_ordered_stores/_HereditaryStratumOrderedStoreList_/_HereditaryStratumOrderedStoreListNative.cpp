// cppimport
#include <cstddef>
#include <variant>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <hstrat/config/HSTRAT_RANK_T.hpp>
#include <hstrat/genome_instrumentation/stratum_ordered_stores/HereditaryStratumOrderedStoreList.hpp>
#include <hstrat_pybind/pyobject.hpp>
#include <hstrat_pybind/shim_py_object_generator.hpp>
#include <hstrat_pybind/custom_casters.hpp>

namespace py = pybind11;

using stratum_t = hstrat::HereditaryStratum<
  uint64_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  HSTRAT_RANK_T // DEPOSITION_RANK_T
>;

using self_t = hstrat::HereditaryStratumOrderedStoreList<stratum_t>;

PYBIND11_MODULE(_HereditaryStratumOrderedStoreListNative, m) {

  // ensure availability of algo::PolicySpec
  // see https://stackoverflow.com/questions/51833291/splitting-up-pybind11-modules-and-issues-with-automatic-type-conversion#comment113430868_51852400
  py::module::import("cppimport.import_hook");
  auto importlib = py::module::import("importlib");
  importlib.attr("import_module")(
    "....._bindings",
    m.attr("__name__")
  );

  py::class_<self_t>(
    m,
    "HereditaryStratumOrderedStoreListNative"
  )
  .def(py::init<>())
  .def("__eq__", &self_t::operator==)
  .def("__copy__", [](const self_t& self){ return self; })
  .def("__deepcopy__", [](const self_t& self, py::object){ return self; })
  .def("Clone", [](const self_t& self){ return self; })
  .def("DepositStratum", [](
      self_t& self,
      const HSTRAT_RANK_T rank,
      const self_t::hereditary_stratum_t& stratum
    ){ self.DepositStratum(rank, stratum); },
    py::arg("rank"),
    py::arg("stratum")
  )
  .def("DepositStratum",
    [](self_t& self, const HSTRAT_RANK_T rank, py::object stratum){
      self.DepositStratum(rank, self_t::hereditary_stratum_t{stratum});
    },
    py::arg("rank"),
    py::arg("stratum")
  )
  .def("GetNumStrataRetained", &self_t::GetNumStrataRetained)
  .def("GetStratumAtColumnIndex",
    [](
      self_t& self, const HSTRAT_RANK_T index, py::object // ignored
    ){ return self.GetStratumAtColumnIndex(index); },
    py::arg("index"),
    py::arg("get_rank_at_column_index") = py::none()
  )
  .def("GetRankAtColumnIndex",
    [](const self_t& self, const HSTRAT_RANK_T index){
      return self.GetRankAtColumnIndex(index);
    }
  )
  .def("GetColumnIndexOfRank",
    [](const self_t& self, const HSTRAT_RANK_T rank){
      return self.GetColumnIndexOfRank(rank);
    }
  )
  .def("DelRanks",
    [](self_t& self, py::object ranks, py::object get_column_index_of_rank){
      if (!get_column_index_of_rank.is_none()) {
        self.DelRanks(
          hstrat_pybind::shim_py_object_generator<const HSTRAT_RANK_T>(ranks),
          [get_column_index_of_rank](const HSTRAT_RANK_T rank){
            return get_column_index_of_rank(
              rank
            ).template cast<HSTRAT_RANK_T>();
          }
        );
      } else {
        self.DelRanks(
          hstrat_pybind::shim_py_object_generator<const HSTRAT_RANK_T>(ranks)
        );
      }
    },
    py::arg("ranks"),
    py::arg("get_column_index_of_rank") = py::none()
  )
  .def("IterRetainedRanks", &self_t::IterRetainedRanks)
  .def("IterRankDifferentia",
    [](
      const self_t& self,
      py::object get_rank_at_column_index,
      const HSTRAT_RANK_T start_column_index
    ){
      if (!get_rank_at_column_index.is_none()) {
        return self.IterRankDifferentia(
          start_column_index,
          [get_rank_at_column_index](const HSTRAT_RANK_T index){
            return get_rank_at_column_index(
              index
            ).template cast<HSTRAT_RANK_T>();
          }
        );
      } else {
        return self.IterRankDifferentia(start_column_index);
      }
    },
    py::arg("get_rank_at_column_index") = py::none(),
    py::arg("start_column_index") = 0
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
