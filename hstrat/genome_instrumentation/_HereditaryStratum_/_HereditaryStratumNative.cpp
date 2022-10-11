// cppimport
#include <cstddef>
#include <variant>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <hstrat/genome_instrumentation/HereditaryStratum.hpp>
#include <hstrat_pybind/pyobject.hpp>
#include <hstrat_pybind/custom_casters.hpp>


namespace py = pybind11;
using namespace pybind11::literals;

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


  py::class_<bit_deporank_t>(
    m,
    "_HereditaryStratumNative_bit_deporank"
  )
  .def("__eq__",
    [](const bit_deporank_t& self, const bit_deporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const bit_deporank_t& self, py::object other){
      return self == bit_deporank_t{other};
    }
  )
  .def("__copy__", [](const bit_deporank_t& self){ return self; })
  .def("__deepcopy__", [](const bit_deporank_t& self, py::object){
    return self;
  })
  .def("GetDifferentia", &bit_deporank_t::GetDifferentia)
  .def("GetDepositionRank", &bit_deporank_t::GetDepositionRank)
  .def("GetAnnotation", &bit_deporank_t::GetAnnotation);

  py::class_<byte_deporank_t>(
    m,
    "_HereditaryStratumNative_byte_deporank"
  )
  .def("__eq__",
    [](const byte_deporank_t& self, const byte_deporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const byte_deporank_t& self, py::object other){
      return self == byte_deporank_t{other};
    }
  )
  .def("__copy__", [](const byte_deporank_t& self){ return self; })
  .def("__deepcopy__", [](const byte_deporank_t& self, py::object){
    return self;
  })
  .def("GetDifferentia", &byte_deporank_t::GetDifferentia)
  .def("GetDepositionRank", &byte_deporank_t::GetDepositionRank)
  .def("GetAnnotation", &byte_deporank_t::GetAnnotation);

  py::class_<word_deporank_t>(
    m,
    "_HereditaryStratumNative_word_deporank"
  )
  .def("__eq__",
    [](const word_deporank_t& self, const word_deporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const word_deporank_t& self, py::object other){
      return self == word_deporank_t{other};
    }
  )
  .def("__copy__", [](const word_deporank_t& self){ return self; })
  .def("__deepcopy__", [](const word_deporank_t& self, py::object){
    return self;
  })
  .def("GetDifferentia", &word_deporank_t::GetDifferentia)
  .def("GetDepositionRank", &word_deporank_t::GetDepositionRank)
  .def("GetAnnotation", &word_deporank_t::GetAnnotation);

  py::class_<doubleword_deporank_t>(
    m,
    "_HereditaryStratumNative_doubleword_deporank"
  )
  .def("__eq__",
    [](const doubleword_deporank_t& self, const doubleword_deporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const doubleword_deporank_t& self, py::object other){
      return self == doubleword_deporank_t{other};
    }
  )
  .def("__copy__", [](const doubleword_deporank_t& self){ return self; })
  .def("__deepcopy__", [](const doubleword_deporank_t& self, py::object){
    return self;
  })
  .def("GetDifferentia", &doubleword_deporank_t::GetDifferentia)
  .def("GetDepositionRank", &doubleword_deporank_t::GetDepositionRank)
  .def("GetAnnotation", &doubleword_deporank_t::GetAnnotation);

  py::class_<quadword_deporank_t>(
    m,
    "_HereditaryStratumNative_quadword_deporank"
  )
  .def("__eq__",
    [](const quadword_deporank_t& self, const quadword_deporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const quadword_deporank_t& self, py::object other){
      return self == quadword_deporank_t{other};
    }
  )
  .def("__copy__", [](const quadword_deporank_t& self){ return self; })
  .def("__deepcopy__", [](const quadword_deporank_t& self, py::object){
    return self;
  })
  .def("GetDifferentia", &quadword_deporank_t::GetDifferentia)
  .def("GetDepositionRank", &quadword_deporank_t::GetDepositionRank)
  .def("GetAnnotation", &quadword_deporank_t::GetAnnotation);


  py::class_<bit_nodeporank_t>(
    m,
    "_HereditaryStratumNative_bit_nodeporank"
  )
  .def("__eq__",
    [](const bit_nodeporank_t& self, const bit_nodeporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const bit_nodeporank_t& self, py::object other){
      return self == bit_nodeporank_t{other};
    }
  )
  .def("__copy__", [](const bit_nodeporank_t& self){ return self; })
  .def("__deepcopy__", [](const bit_nodeporank_t& self, py::object){
    return self;
  })
  .def("GetDifferentia", &bit_nodeporank_t::GetDifferentia)
  .def("GetDepositionRank", [](const bit_nodeporank_t&){ return py::none(); })
  .def("GetAnnotation", &bit_nodeporank_t::GetAnnotation);

  py::class_<byte_nodeporank_t>(
    m,
    "_HereditaryStratumNative_byte_nodeporank"
  )
  .def("__eq__",
    [](const byte_nodeporank_t& self, const byte_nodeporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const byte_nodeporank_t& self, py::object other){
      return self == byte_nodeporank_t{other};
    }
  )
  .def("__copy__", [](const byte_nodeporank_t& self){ return self; })
  .def("__deepcopy__", [](const byte_nodeporank_t& self, py::object){
    return self;
  })
  .def("GetDifferentia", &byte_nodeporank_t::GetDifferentia)
  .def("GetDepositionRank", [](const byte_nodeporank_t&){ return py::none(); })
  .def("GetAnnotation", &byte_nodeporank_t::GetAnnotation);

  py::class_<word_nodeporank_t>(
    m,
    "_HereditaryStratumNative_word_nodeporank"
  )
  .def("__eq__",
    [](const word_nodeporank_t& self, const word_nodeporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const word_nodeporank_t& self, py::object other){
      return self == word_nodeporank_t{other};
    }
  )
  .def("__copy__", [](const word_nodeporank_t& self){ return self; })
  .def("__deepcopy__", [](const word_nodeporank_t& self, py::object){
    return self;
  })
  .def("GetDifferentia", &word_nodeporank_t::GetDifferentia)
  .def("GetDepositionRank", [](const word_nodeporank_t&){ return py::none(); })
  .def("GetAnnotation", &word_nodeporank_t::GetAnnotation);

  py::class_<doubleword_nodeporank_t>(
    m,
    "_HereditaryStratumNative_doubleword_nodeporank"
  )
  .def("__eq__",
    [](const doubleword_nodeporank_t& self, const doubleword_nodeporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const doubleword_nodeporank_t& self, py::object other){
      return self == doubleword_nodeporank_t{other};
    }
  )
  .def("__copy__", [](const doubleword_nodeporank_t& self){ return self; })
  .def("__deepcopy__", [](const doubleword_nodeporank_t& self, py::object){
    return self;
  })
  .def("GetDifferentia", &doubleword_nodeporank_t::GetDifferentia)
  .def("GetDepositionRank", [](const doubleword_nodeporank_t&){
    return py::none();
  })
  .def("GetAnnotation", &doubleword_nodeporank_t::GetAnnotation);

  py::class_<quadword_nodeporank_t>(
    m,
    "_HereditaryStratumNative_quadword_nodeporank"
  )
  .def("__eq__",
    [](const quadword_nodeporank_t& self, const quadword_nodeporank_t& other){
      return self == other;
    }
  )
  .def("__eq__",
    [](const quadword_nodeporank_t& self, py::object other){
      return self == quadword_nodeporank_t{other};
    }
  )
  .def("__copy__", [](const quadword_nodeporank_t& self){ return self; })
  .def("__deepcopy__", [](const quadword_nodeporank_t& self, py::object){ return self; })
  .def("GetDifferentia", &quadword_nodeporank_t::GetDifferentia)
  .def("GetDepositionRank", [](const quadword_nodeporank_t&){
    return py::none();
  })
  .def("GetAnnotation", &quadword_nodeporank_t::GetAnnotation);

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
