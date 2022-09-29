#pragma once
#ifndef HSTRAT_PYBIND_PYOBJECTPOLICYSHIM_HPP_INCLUDE
#define HSTRAT_PYBIND_PYOBJECTPOLICYSHIM_HPP_INCLUDE

#include <pybind11/pybind11.h>

namespace py = pybind11;

#include "../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../hstrat/config/HSTRAT_RANK_T.hpp"

#include "shim_py_object_generator.hpp"

namespace hstrat_pybind {

template<typename POLICY_SPEC>
class PyObjectPolicyShim {

  py::object policy_obj;

public:

  PyObjectPolicyShim(py::object policy_obj) : policy_obj(policy_obj) {}

  auto GetSpec() const {
    auto spec_obj = policy_obj.attr("GetSpec")();
    auto spec = POLICY_SPEC{spec_obj};
    return spec;
  }

  // enactment
  cppcoro::generator<const HSTRAT_RANK_T> GenDropRanks(
    const HSTRAT_RANK_T num_stratum_depositions_completed,
    cppcoro::generator<const HSTRAT_RANK_T> retained_ranks
  ) {
    return shim_py_object_generator<const HSTRAT_RANK_T>(
      policy_obj.attr("GenDropRanks")(
        num_stratum_depositions_completed,
        retained_ranks
      )
    );
  }

  // invariants
  // CalcMrcaUncertaintyAbsUpperBound
  // CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank
  // CalcMrcaUncertaintyAbsUpperBoundPessimalRank
  // CalcMrcaUncertaintyRelUpperBoundAtPessimalRank
  // CalcMrcaUncertaintyRelUpperBoundPessimalRank
  // CalcNumStrataRetainedUpperBound

  // scrying
  // CalcMrcaUncertaintyAbsExact
  // CalcMrcaUncertaintyRelExact
  // CalcNumStrataRetainedExact
  // CalcRankAtColumnIndex
  // IterRetainedRanks

};

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_PYBIND_PYOBJECTPOLICYSHIM_HPP_INCLUDE
