// cppimport
#include <cstddef>
#include <tuple>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cppcoro/include/cppcoro/generator.hpp>

#include <hstrat/config/HSTRAT_RANK_T.hpp>

namespace py = pybind11;

PYBIND11_MODULE(_CppcoroGenerator, m) {

  using rank_generator_t = cppcoro::generator<const HSTRAT_RANK_T>;
  py::class_<rank_generator_t>(
    m,
    "CppcoroGeneratorHstratRankT"
  )
  .def(
    "__iter__",
    [](rank_generator_t& self) {
      return py::make_iterator(self.begin(), self.end());
    },
    py::keep_alive<0, 1>()
  )
  .def(
    "__next__",
    [](rank_generator_t& self) {
      auto iter = self.begin();
      if (iter == self.end()) throw py::stop_iteration{};

      const auto res = *iter;
      ++iter;
      return res;
    }
  );

  using bool_tuple_t = std::tuple<HSTRAT_RANK_T, bool>;
  using bool_tuple_generator_t = cppcoro::generator<bool_tuple_t>;
  py::class_<bool_tuple_generator_t>(
    m,
    "CppcoroGeneratorHstratRankBoolTupleT"
  )
  .def(
    "__iter__",
    [](bool_tuple_generator_t& self) {
      return py::make_iterator(self.begin(), self.end());
    },
    py::keep_alive<0, 1>()
  )
  .def(
    "__next__",
    [](bool_tuple_generator_t& self) {
      auto iter = self.begin();
      if (iter == self.end()) throw py::stop_iteration{};

      const auto res = *iter;
      ++iter;
      return res;
    }
  );

  using byte_tuple_t = std::tuple<HSTRAT_RANK_T, uint8_t>;
  using byte_tuple_generator_t = cppcoro::generator<byte_tuple_t>;
  py::class_<byte_tuple_generator_t>(
    m,
    "CppcoroGeneratorHstratRankByteTupleT"
  )
  .def(
    "__iter__",
    [](byte_tuple_generator_t& self) {
      return py::make_iterator(self.begin(), self.end());
    },
    py::keep_alive<0, 1>()
  )
  .def(
    "__next__",
    [](byte_tuple_generator_t& self) {
      auto iter = self.begin();
      if (iter == self.end()) throw py::stop_iteration{};

      const auto res = *iter;
      ++iter;
      return res;
    }
  );

  using word_tuple_t = std::tuple<HSTRAT_RANK_T, uint16_t>;
  using word_tuple_generator_t = cppcoro::generator<word_tuple_t>;
  py::class_<word_tuple_generator_t>(
    m,
    "CppcoroGeneratorHstratRankWordTupleT"
  )
  .def(
    "__iter__",
    [](word_tuple_generator_t& self) {
      return py::make_iterator(self.begin(), self.end());
    },
    py::keep_alive<0, 1>()
  )
  .def(
    "__next__",
    [](word_tuple_generator_t& self) {
      auto iter = self.begin();
      if (iter == self.end()) throw py::stop_iteration{};

      const auto res = *iter;
      ++iter;
      return res;
    }
  );

  using doubleword_tuple_t = std::tuple<HSTRAT_RANK_T, uint32_t>;
  using doubleword_tuple_generator_t = cppcoro::generator<doubleword_tuple_t>;
  py::class_<doubleword_tuple_generator_t>(
    m,
    "CppcoroGeneratorHstratRankDoubleWordTupleT"
  )
  .def(
    "__iter__",
    [](doubleword_tuple_generator_t& self) {
      return py::make_iterator(self.begin(), self.end());
    },
    py::keep_alive<0, 1>()
  )
  .def(
    "__next__",
    [](doubleword_tuple_generator_t& self) {
      auto iter = self.begin();
      if (iter == self.end()) throw py::stop_iteration{};

      const auto res = *iter;
      ++iter;
      return res;
    }
  );

  using quadword_tuple_t = std::tuple<HSTRAT_RANK_T, uint64_t>;
  using quadword_tuple_generator_t = cppcoro::generator<quadword_tuple_t>;
  py::class_<quadword_tuple_generator_t>(
    m,
    "CppcoroGeneratorHstratRankQuadWordTupleT"
  )
  .def(
    "__iter__",
    [](quadword_tuple_generator_t& self) {
      return py::make_iterator(self.begin(), self.end());
    },
    py::keep_alive<0, 1>()
  )
  .def(
    "__next__",
    [](quadword_tuple_generator_t& self) {
      auto iter = self.begin();
      if (iter == self.end()) throw py::stop_iteration{};

      const auto res = *iter;
      ++iter;
      return res;
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
cfg['include_dirs'] = [f'{root_dir}/include', f'{root_dir}/third-party']

setup_pybind11(cfg)
%>
*/
