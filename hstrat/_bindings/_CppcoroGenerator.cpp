// cppimport
#include <pybind11/pybind11.h>

#include <cppcoro/include/cppcoro/generator.hpp>

namespace py = pybind11;

PYBIND11_MODULE(_CppcoroGenerator, m) {

  using int_generator_t = cppcoro::generator<const int>;
  py::class_<int_generator_t>(
    m,
    "CppcoroGeneratorInt"
  )
  .def(
    "__iter__",
    [](int_generator_t& self) {
      return py::make_iterator(self.begin(), self.end());
    },
    py::keep_alive<0, 1>()
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
