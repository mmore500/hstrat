// cppimport
#include <cstddef>
#include <tuple>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cppcoro/include/cppcoro/generator.hpp>

#include <hstrat_auxlib/DerefAsValueIterator.hpp>
#include <hstrat/config/HSTRAT_RANK_T.hpp>
#include <hstrat/genome_instrumentation/HereditaryStratum.hpp>
#include <hstrat_pybind/all_tu_declarations.hpp>

namespace py = pybind11;

#define INSTANCE(SELF_T) py::class_<SELF_T>(\
  m,\
  "CppcoroGeneratorHstrat" #SELF_T\
)\
.def(\
  "__iter__",\
  [](SELF_T& self) {\
    return py::make_iterator(self.begin(), self.end());\
  },\
  py::keep_alive<0, 1>()\
)

// don't wrap end because it's a sentinel
#define INSTANCE_DEREF_AS_VALUE(SELF_T) py::class_<SELF_T>(\
  m,\
  "CppcoroGeneratorHstratDerefAsValue" #SELF_T\
)\
.def(\
  "__iter__",\
  [](SELF_T& self) {\
    return py::make_iterator(\
      hstrat_auxlib::make_deref_as_value_iterator(self.begin()),\
      self.end(),\
      py::return_value_policy::move\
    );\
  },\
  py::keep_alive<0, 1>()\
)


PYBIND11_MODULE(_CppcoroGenerator, m) {

  using rank_generator_t = cppcoro::generator<const HSTRAT_RANK_T>;
  INSTANCE(rank_generator_t);

  using bool_tuple_t = std::tuple<HSTRAT_RANK_T, bool>;
  using bool_tuple_generator_t = cppcoro::generator<bool_tuple_t>;
  INSTANCE_DEREF_AS_VALUE(bool_tuple_generator_t);

  using byte_tuple_t = std::tuple<HSTRAT_RANK_T, uint8_t>;
  using byte_tuple_generator_t = cppcoro::generator<byte_tuple_t>;
  INSTANCE_DEREF_AS_VALUE(byte_tuple_generator_t);

  using word_tuple_t = std::tuple<HSTRAT_RANK_T, uint16_t>;
  using word_tuple_generator_t = cppcoro::generator<word_tuple_t>;
  INSTANCE_DEREF_AS_VALUE(word_tuple_generator_t);

  using doubleword_tuple_t = std::tuple<HSTRAT_RANK_T, uint32_t>;
  using doubleword_tuple_generator_t = cppcoro::generator<doubleword_tuple_t>;
  INSTANCE_DEREF_AS_VALUE(doubleword_tuple_generator_t);

  using quadword_tuple_t = std::tuple<HSTRAT_RANK_T, uint64_t>;
  using quadword_tuple_generator_t = cppcoro::generator<quadword_tuple_t>;
  INSTANCE_DEREF_AS_VALUE(quadword_tuple_generator_t);

  using bit_deporank_statum_t = hstrat::HereditaryStratum<
    bool, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using bit_deporank_generator_t = cppcoro::generator<bit_deporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(bit_deporank_generator_t);

  using byte_deporank_statum_t = hstrat::HereditaryStratum<
    uint8_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using byte_deporank_generator_t = cppcoro::generator<byte_deporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(byte_deporank_generator_t);

  using word_deporank_statum_t = hstrat::HereditaryStratum<
    uint16_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using word_deporank_generator_t = cppcoro::generator<word_deporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(word_deporank_generator_t);

  using doubleword_deporank_statum_t = hstrat::HereditaryStratum<
    uint32_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using doubleword_deporank_generator_t = cppcoro::generator<
    doubleword_deporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(doubleword_deporank_generator_t);

  using quadword_deporank_statum_t = hstrat::HereditaryStratum<
    uint64_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using quadword_deporank_generator_t = cppcoro::generator<
    quadword_deporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(quadword_deporank_generator_t);

  using bit_nodeporank_statum_t = hstrat::HereditaryStratum<
    bool, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using bit_nodeporank_generator_t = cppcoro::generator<
    bit_nodeporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(bit_nodeporank_generator_t);

  using byte_nodeporank_statum_t = hstrat::HereditaryStratum<
    uint8_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using byte_nodeporank_generator_t = cppcoro::generator<
    byte_nodeporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(byte_nodeporank_generator_t);

  using word_nodeporank_statum_t = hstrat::HereditaryStratum<
    uint16_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using word_nodeporank_generator_t = cppcoro::generator<
    word_nodeporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(word_nodeporank_generator_t);

  using doubleword_nodeporank_statum_t = hstrat::HereditaryStratum<
    uint32_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using doubleword_nodeporank_generator_t = cppcoro::generator<
    doubleword_nodeporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(doubleword_nodeporank_generator_t);

  using quadword_nodeporank_statum_t = hstrat::HereditaryStratum<
    uint64_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using quadword_nodeporank_generator_t = cppcoro::generator<
    quadword_nodeporank_statum_t>;
  INSTANCE_DEREF_AS_VALUE(quadword_nodeporank_generator_t);


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
