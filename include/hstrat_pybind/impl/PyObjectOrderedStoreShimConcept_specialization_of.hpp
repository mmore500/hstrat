#pragma once
#ifndef HSTRAT_PYBIND_IMPL_PYOBJECTORDEREDSTORESHIMCONCEPT_SPECIALIZATION_OF_HPP_INCLUDE
#define HSTRAT_PYBIND_IMPL_PYOBJECTORDEREDSTORESHIMCONCEPT_SPECIALIZATION_OF_HPP_INCLUDE

#include "../PyObjectOrderedStoreShim.hpp"

namespace hstrat_pybind {

template<class T> concept PyObjectOrderedStoreShimConcept = (
  hstrat_auxlib::is_specialization_of<
    hstrat_pybind::PyObjectOrderedStoreShim,
    T
  >::value
);

} // namespace hstrat_pybind

#endif // #ifndef HSTRAT_PYBIND_IMPL_PYOBJECTORDEREDSTORESHIMCONCEPT_SPECIALIZATION_OF_HPP_INCLUDE
