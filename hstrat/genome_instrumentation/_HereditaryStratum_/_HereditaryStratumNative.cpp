// cppimport
#include <cstddef>
#include <variant>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <hstrat/genome_instrumentation/HereditaryStratum.hpp>
#include <hstrat_pybind/all_tu_declarations.hpp>
#include <hstrat_pybind/pyobject.hpp>


namespace py = pybind11;
using namespace pybind11::literals;

#define INSTANCE_DEPORANK(SELF_T) py::class_<SELF_T>(\
    m,\
    "_HereditaryStratumNative_" #SELF_T\
  )\
  .def("__eq__",\
    [](const SELF_T& self, const SELF_T& other){\
      return self == other;\
    }\
  )\
  .def("__eq__",\
    [](const SELF_T& self, py::object other){\
      return self == SELF_T{other};\
    }\
  )\
  .def("__copy__", [](const SELF_T& self){ return self; })\
  .def("__deepcopy__", [](const SELF_T& self, py::object){\
    return self;\
  })\
  .def("GetDifferentia", &SELF_T::GetDifferentia)\
  .def("GetDepositionRank", &SELF_T::GetDepositionRank)\
  .def("GetAnnotation", [](const SELF_T& self) -> py::object {\
    return self.GetAnnotation();\
  })

#define INSTANCE_NODEPORANK(SELF_T) py::class_<SELF_T>(\
    m,\
    "_HereditaryStratumNative_" #SELF_T\
  )\
  .def("__eq__",\
    [](const SELF_T& self, const SELF_T& other){\
      return self == other;\
    }\
  )\
  .def("__eq__",\
    [](const SELF_T& self, py::object other){\
      return self == SELF_T{other};\
    }\
  )\
  .def("__copy__", [](const SELF_T& self){ return self; })\
  .def("__deepcopy__", [](const SELF_T& self, py::object){\
    return self;\
  })\
  .def("GetDifferentia", &SELF_T::GetDifferentia)\
  .def("GetDepositionRank",\
    [](const SELF_T&){ return py::none(); }\
  )\
  .def("GetAnnotation", [](const SELF_T& self) -> py::object {\
    return self.GetAnnotation();\
  })

using bit_deporank_t = hstrat::HereditaryStratum<
  bool, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  HSTRAT_RANK_T // DEPOSITION_RANK_T
>;

using byte_deporank_t = hstrat::HereditaryStratum<
  uint8_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  HSTRAT_RANK_T // DEPOSITION_RANK_T
>;

using word_deporank_t = hstrat::HereditaryStratum<
  uint16_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  HSTRAT_RANK_T // DEPOSITION_RANK_T
>;

using doubleword_deporank_t = hstrat::HereditaryStratum<
  uint32_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  HSTRAT_RANK_T // DEPOSITION_RANK_T
>;

using quadword_deporank_t = hstrat::HereditaryStratum<
  uint64_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  HSTRAT_RANK_T // DEPOSITION_RANK_T
>;

using bit_nodeporank_t = hstrat::HereditaryStratum<
  bool, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using byte_nodeporank_t = hstrat::HereditaryStratum<
  uint8_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using word_nodeporank_t = hstrat::HereditaryStratum<
  uint16_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using doubleword_nodeporank_t = hstrat::HereditaryStratum<
  uint32_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using quadword_nodeporank_t = hstrat::HereditaryStratum<
  uint64_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

PYBIND11_MODULE(_HereditaryStratumNative, m) {

  m.def("HereditaryStratumNative", [](
      py::object annotation,
      const int64_t differentia_bit_width,
      py::object deposition_rank
    ) -> std::variant<
      bit_deporank_t, byte_deporank_t, word_deporank_t, doubleword_deporank_t, quadword_deporank_t,
      bit_nodeporank_t, byte_nodeporank_t, word_nodeporank_t, doubleword_nodeporank_t, quadword_nodeporank_t
    > {

      if (differentia_bit_width == 1 && deposition_rank.is_none()) {
        return bit_nodeporank_t(
          HSTRAT_RANK_T{}, // arbitrary, will be ignored
          annotation
        );
      }
      else if (differentia_bit_width == 8 && deposition_rank.is_none()) {
        return byte_nodeporank_t(
          HSTRAT_RANK_T{}, // arbitrary, will be ignored
          annotation
        );
      }
      else if (differentia_bit_width == 16 && deposition_rank.is_none()) {
        return word_nodeporank_t(
          HSTRAT_RANK_T{}, // arbitrary, will be ignored
          annotation
        );
      }
      else if (differentia_bit_width == 32 && deposition_rank.is_none()) {
        return doubleword_nodeporank_t(
          HSTRAT_RANK_T{}, // arbitrary, will be ignored
          annotation
        );
      }
      else if (differentia_bit_width == 64 && deposition_rank.is_none()) {
        return quadword_nodeporank_t(
          HSTRAT_RANK_T{}, // arbitrary, will be ignored
          annotation
        );
      }
      else if (differentia_bit_width == 1 && !deposition_rank.is_none()) {
        return bit_deporank_t(
          deposition_rank.template cast<HSTRAT_RANK_T>(),
          annotation
        );
      }
      else if (differentia_bit_width == 8 && !deposition_rank.is_none()) {
        return byte_deporank_t(
          deposition_rank.template cast<HSTRAT_RANK_T>(),
          annotation
        );
      }
      else if (differentia_bit_width == 16 && !deposition_rank.is_none()) {
        return word_deporank_t(
          deposition_rank.template cast<HSTRAT_RANK_T>(),
          annotation
        );
      }
      else if (differentia_bit_width == 32 && !deposition_rank.is_none()) {
        return doubleword_deporank_t(
          deposition_rank.template cast<HSTRAT_RANK_T>(),
          annotation
        );
      }
      else if (differentia_bit_width == 64 && !deposition_rank.is_none()) {
        return quadword_deporank_t(
          deposition_rank.template cast<HSTRAT_RANK_T>(),
          annotation
        );
      }
      else throw std::invalid_argument{"unsupported differentia bit width"};
    },
    py::kw_only(),
    py::arg("annotation") = py::none(),
    py::arg("differentia_bit_width") = 64,
    py::arg("deposition_rank") = py::none()
  );

  INSTANCE_DEPORANK(bit_deporank_t);
  INSTANCE_DEPORANK(byte_deporank_t);
  INSTANCE_DEPORANK(word_deporank_t);
  INSTANCE_DEPORANK(doubleword_deporank_t);
  INSTANCE_DEPORANK(quadword_deporank_t);

  INSTANCE_NODEPORANK(bit_nodeporank_t);
  INSTANCE_NODEPORANK(byte_nodeporank_t);
  INSTANCE_NODEPORANK(word_nodeporank_t);
  INSTANCE_NODEPORANK(doubleword_nodeporank_t);
  INSTANCE_NODEPORANK(quadword_nodeporank_t);

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
