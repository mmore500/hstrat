#pragma once
#ifndef HSTRAT_AUXLIB_DEEPCOPY_HPP_INCLUDE
#define HSTRAT_AUXLIB_DEEPCOPY_HPP_INCLUDE

#include <algorithm>
#include <type_traits>

#include "../hstrat_pybind/deepcopy.hpp"
#include "../hstrat_pybind/pybind11_or_stubs.hpp"
#include "../hstrat_pybind/PyObjectConcept.hpp"

#include "Cloneable.hpp"
#include "Container.hpp"
#include "TriviallyCopyable.hpp"

namespace py = pybind11;

namespace hstrat_auxlib {

  decltype(auto) deepcopy(hstrat_auxlib::TriviallyCopyable auto obj) {
    return obj;
  }

  decltype(auto) deepcopy(hstrat_auxlib::Cloneable auto obj) {
    return obj.Clone();
  }

  decltype(auto) deepcopy(py::object obj) {
    return hstrat_pybind::deepcopy(obj);
  }

  decltype(auto) deepcopy(hstrat_auxlib::Container auto container) {
    using container_t = decltype(container);
    container_t output(std::size(container));
    using value_type = typename container_t::value_type;
    std::transform(
      std::begin(container),
      std::end(container),
      std::begin(output),
      deepcopy<value_type>
    );
    return output;
  }

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_AUXLIB_DEEPCOPY_HPP_INCLUDE
