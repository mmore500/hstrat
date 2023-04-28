// cppimport
#include <assert.h>
#include <cstddef>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cppcoro/include/cppcoro/generator.hpp>

#include <hstrat_auxlib/Monostate.hpp>
#include <hstrat/config/HSTRAT_RANK_T.hpp>
#include <hstrat/genome_instrumentation/stratum_ordered_stores/HereditaryStratumOrderedStoreList.hpp>
#include <hstrat_pybind/all_tu_declarations.hpp>
#include <hstrat_pybind/pyobject.hpp>
#include <hstrat_pybind/shim_py_object_generator.hpp>

namespace py = pybind11;

#define INSTANCE(SELF_T, PASTEON) py::class_<SELF_T>(\
  m,\
  "HereditaryStratumOrderedStoreListNative" #PASTEON\
)\
.def(py::init<>())\
.def("__eq__", &SELF_T::operator==)\
.def("__copy__", [](const SELF_T& self){ return self; })\
.def("Clone", [](const SELF_T& self){ return self; })\
.def("DepositStratum", [](\
    SELF_T& self,\
    const HSTRAT_RANK_T rank,\
    const SELF_T::hereditary_stratum_t& stratum\
  ){ self.DepositStratum(rank, stratum); },\
  py::arg("rank"),\
  py::arg("stratum")\
)\
.def("DepositStratum",\
  [](SELF_T& self, const HSTRAT_RANK_T rank, py::object stratum){\
    self.DepositStratum(rank, SELF_T::hereditary_stratum_t{stratum});\
  },\
  py::arg("rank"),\
  py::arg("stratum")\
)\
.def("GetNumStrataRetained", &SELF_T::GetNumStrataRetained)\
.def("GetStratumAtColumnIndex",\
  [](\
    SELF_T& self, const HSTRAT_RANK_T index, py::object\
  ){ return self.GetStratumAtColumnIndex(index); },\
  py::arg("index"),\
  py::arg("get_rank_at_column_index") = py::none()\
)\
.def(\
  "IterRetainedStrata", [](SELF_T& self){\
    return self.IterRetainedStrata();\
  }, py::keep_alive<0, 1>()\
)\

PYBIND11_MODULE(_HereditaryStratumOrderedStoreListNative, m) {

  // ensure availability of algo::PolicySpec
  // see https://stackoverflow.com/questions/51833291/splitting-up-pybind11-modules-and-issues-with-automatic-type-conversion#comment113430868_51852400
  py::module::import("cppimport.import_hook");
  auto importlib = py::module::import("importlib");
  importlib.attr("import_module")(
    "....._bindings",
    m.attr("__name__")
  );
  importlib.attr("import_module")(
    "...._HereditaryStratum_._HereditaryStratumNative",
    m.attr("__name__")
  );

  const auto import_module = py::module::import("importlib").attr(
    "import_module"
  );
  const auto HereditaryStratumOrderedStoreABC_register = import_module(
    "..._detail", m.attr("__name__")
  ).attr("HereditaryStratumOrderedStoreABC").attr("register");

  using stratum_deporank_t = hstrat::HereditaryStratum<
    uint64_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using store_deporank_t = hstrat::HereditaryStratumOrderedStoreList<
    stratum_deporank_t
  >;
  HereditaryStratumOrderedStoreABC_register(
    INSTANCE(store_deporank_t, )
    .def("IterRankDifferentiaZip",
      [](
        const store_deporank_t& self,
        py::object get_rank_at_column_index,
        const HSTRAT_RANK_T start_column_index
      ){
        if (!get_rank_at_column_index.is_none()) {
          return self.IterRankDifferentiaZip(
            start_column_index,
            [get_rank_at_column_index](const HSTRAT_RANK_T index){
              return get_rank_at_column_index(
                index
              ).template cast<HSTRAT_RANK_T>();
            }
          );
        } else {
          return self.IterRankDifferentiaZip(start_column_index);
        }
      },
      py::arg("get_rank_at_column_index") = py::none(),
      py::arg("start_column_index") = 0,
      py::keep_alive<0, 1>()
    )
    .def("DelRanks",
      [](
        store_deporank_t& self,
        py::object ranks,
        py::object get_column_index_of_rank
      ){
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
    .def(
      "IterRetainedRanks", &store_deporank_t::IterRetainedRanks,
      py::keep_alive<0, 1>()
    )
    .def("GetRankAtColumnIndex",
      [](const store_deporank_t& self, const HSTRAT_RANK_T index){
        return self.GetRankAtColumnIndex(index);
      }
    )
    .def("GetColumnIndexOfRank",
      [](const store_deporank_t& self, const HSTRAT_RANK_T rank){
        return self.GetColumnIndexOfRank(rank);
      }
    )
  );

  using stratum_nodeporank_t = hstrat::HereditaryStratum<
    uint64_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    hstrat_auxlib::Monostate // DEPOSITION_RANK_T
  >;
  using store_nodeporank_t = hstrat::HereditaryStratumOrderedStoreList<
    stratum_nodeporank_t
  >;
  HereditaryStratumOrderedStoreABC_register(
    INSTANCE(store_nodeporank_t, _NoDepoRank)
    .def("IterRankDifferentiaZip",
      [](
        const store_nodeporank_t& self,
        py::object get_rank_at_column_index,
        const HSTRAT_RANK_T start_column_index
      ){
        return self.IterRankDifferentiaZip(
          start_column_index,
          [get_rank_at_column_index](const HSTRAT_RANK_T index){
            return get_rank_at_column_index(
              index
            ).template cast<HSTRAT_RANK_T>();
          }
        );
      },
      py::arg("get_rank_at_column_index") = py::none(),
      py::arg("start_column_index") = 0,
      py::keep_alive<0, 1>()
    )
    .def("DelRanks",
      [](
        store_nodeporank_t& self,
        py::object ranks,
        py::object get_column_index_of_rank
      ){
        self.DelRanks(
          hstrat_pybind::shim_py_object_generator<const HSTRAT_RANK_T>(ranks),
          [get_column_index_of_rank](const HSTRAT_RANK_T rank){
            return get_column_index_of_rank(
              rank
            ).template cast<HSTRAT_RANK_T>();
          }
        );
      },
      py::arg("ranks"),
      py::arg("get_column_index_of_rank") = py::none()
    )
    .def(
      "IterRetainedRanks", [](const store_nodeporank_t&){
        return cppcoro::generator<const HSTRAT_RANK_T>{};
      }
    )
    .def("GetRankAtColumnIndex",
      [](const store_nodeporank_t& self, const HSTRAT_RANK_T index){
        assert(false);
        return py::none();
      }
    )
    .def("GetColumnIndexOfRank",
      [](const store_nodeporank_t& self, const HSTRAT_RANK_T rank){
        return py::none();
      }
    )
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

cfg['extra_compile_args'] = ['-std=c++20', '-DFMT_HEADER_ONLY']
cfg['force_rebuild'] = True
cfg['include_dirs'] = [f'{root_dir}/include', f'{root_dir}/third-party']

setup_pybind11(cfg)
%>
*/
