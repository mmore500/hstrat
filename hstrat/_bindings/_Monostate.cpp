// cppimport
#include <pybind11/pybind11.h>

#include <hstrat_auxlib/Monostate.hpp>
#include <hstrat_pybind/all_tu_declarations.hpp>

namespace py = pybind11;

PYBIND11_MODULE(_Monostate, m) {

py::class_<hstrat_auxlib::Monostate>(
  m,
  "Monostate"
)
.def(py::init<>());

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
