// cppimport
#include <cstddef>
#include <tuple>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cppcoro/include/cppcoro/generator.hpp>

#include <hstrat/config/HSTRAT_RANK_T.hpp>
#include <hstrat_pybind/all_tu_declarations.hpp>

namespace py = pybind11;

#define INSTANCE(SELF_T) py::class_<SELF_T>(\
  m,\
  "CppcoroGeneratorHstratRankT" #SELF_T\
)\
.def(\
  "__iter__",\
  [](SELF_T& self) {\
    return py::make_iterator(self.begin(), self.end());\
  },\
  py::keep_alive<0, 1>()\
)

PYBIND11_MODULE(_CppcoroGenerator, m) {

  using rank_generator_t = cppcoro::generator<const HSTRAT_RANK_T>;
  INSTANCE(rank_generator_t);

  using bool_tuple_t = std::tuple<HSTRAT_RANK_T, bool>;
  using bool_tuple_generator_t = cppcoro::generator<bool_tuple_t>;
  INSTANCE(bool_tuple_generator_t);

  using byte_tuple_t = std::tuple<HSTRAT_RANK_T, uint8_t>;
  using byte_tuple_generator_t = cppcoro::generator<byte_tuple_t>;
  INSTANCE(byte_tuple_generator_t);

  using word_tuple_t = std::tuple<HSTRAT_RANK_T, uint16_t>;
  using word_tuple_generator_t = cppcoro::generator<word_tuple_t>;
  INSTANCE(word_tuple_generator_t);

  using doubleword_tuple_t = std::tuple<HSTRAT_RANK_T, uint32_t>;
  using doubleword_tuple_generator_t = cppcoro::generator<doubleword_tuple_t>;
  INSTANCE(doubleword_tuple_generator_t);

  using quadword_tuple_t = std::tuple<HSTRAT_RANK_T, uint64_t>;
  using quadword_tuple_generator_t = cppcoro::generator<quadword_tuple_t>;
  INSTANCE(quadword_tuple_generator_t);

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
