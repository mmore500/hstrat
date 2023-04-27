#pragma once
#ifndef HSTRAT_PYBIND_IMPL_PYBIND11_STUBS_HPP_INCLUDE
#define HSTRAT_PYBIND_IMPL_PYBIND11_STUBS_HPP_INCLUDE

namespace pybind11 {

  struct object {
    template <typename ...Args> object attr(Args && ...args) { return {}; }
  };

  struct module {
    template <typename ...Args> object import(Args && ...args) { return {}; }
  };

};

#endif // #ifndef HSTRAT_PYBIND_IMPL_PYBIND11_STUBS_HPP_INCLUDE
