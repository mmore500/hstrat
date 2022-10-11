#pragma once
#ifndef HSTRAT_PYBIND_PYOBJECTPOLICYSHIM_HPP_INCLUDE
#define HSTRAT_PYBIND_PYOBJECTPOLICYSHIM_HPP_INCLUDE

#include <type_traits>
#include <utility>

#include <pybind11/pybind11.h>

namespace py = pybind11;

#include "../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../hstrat/config/HSTRAT_RANK_T.hpp"

#include "deepcopy.hpp"
#include "shim_py_object_generator.hpp"

namespace hstrat_pybind {

template<
  typename POLICY_SPEC,
  typename HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX=std::true_type,
  typename HAS_SCRY_OTHER=std::true_type
>
class PyObjectPolicyShim {

  py::object policy_obj;

public:

  using spec_t = POLICY_SPEC;

  consteval static bool has_calc_rank_at_column_index() {
    return HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX::value;
  }

  consteval static bool has_iter_retained_ranks() {
    return HAS_SCRY_OTHER::value;
  }

  PyObjectPolicyShim(const PyObjectPolicyShim& other)
  : policy_obj(hstrat_pybind::deepcopy(other.policy_obj))
  {}

  PyObjectPolicyShim(py::object policy_obj) : policy_obj(policy_obj) {}

  bool operator==(const PyObjectPolicyShim& other) const {
    return policy_obj.equal(other.policy_obj);
  }

  auto GetSpec() const {
    auto spec_obj = policy_obj.attr("GetSpec")();
    auto spec = POLICY_SPEC{spec_obj};
    return spec;
  }

  // enactment
  cppcoro::generator<const HSTRAT_RANK_T> GenDropRanks(
    const HSTRAT_RANK_T num_stratum_depositions_completed,
    cppcoro::generator<const HSTRAT_RANK_T> retained_ranks
  ) const {
    return shim_py_object_generator<const HSTRAT_RANK_T>(
      policy_obj.attr("GenDropRanks")(
        num_stratum_depositions_completed,
        std::move(retained_ranks)
      )
    );
  }

  // invariants
  HSTRAT_RANK_T CalcMrcaUncertaintyAbsUpperBound(
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ) const {
    return policy_obj.attr("CalcMrcaUncertaintyAbsUpperBound")(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    ).template cast<HSTRAT_RANK_T>();
  }

  HSTRAT_RANK_T CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ) const {
    return policy_obj.attr("CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank")(
      first_num_strata_deposited,
      second_num_strata_deposited
    ).template cast<HSTRAT_RANK_T>();
  }

  HSTRAT_RANK_T CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ) const {
    return policy_obj.attr("CalcMrcaUncertaintyAbsUpperBoundPessimalRank")(
      first_num_strata_deposited,
      second_num_strata_deposited
    ).template cast<HSTRAT_RANK_T>();
  }

  double CalcMrcaUncertaintyRelUpperBound(
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ) const {
    return policy_obj.attr("CalcMrcaUncertaintyRelUpperBound")(
      first_num_strata_deposited,
      second_num_strata_deposited,
      actual_rank_of_mrca
    ).template cast<double>();
  }

  double CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ) const {
    return policy_obj.attr("CalcMrcaUncertaintyRelUpperBoundAtPessimalRank")(
      first_num_strata_deposited,
      second_num_strata_deposited
    ).template cast<double>();
  }

  HSTRAT_RANK_T CalcMrcaUncertaintyRelUpperBoundPessimalRank(
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited
  ) const {
    return policy_obj.attr("CalcMrcaUncertaintyRelUpperBoundPessimalRank")(
      first_num_strata_deposited,
      second_num_strata_deposited
    ).template cast<HSTRAT_RANK_T>();
  }

  // scrying
  HSTRAT_RANK_T CalcMrcaUncertaintyAbsExact(
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ) const {
    if constexpr (HAS_SCRY_OTHER::value) {
      return policy_obj.attr("CalcMrcaUncertaintyAbsExact")(
        first_num_strata_deposited,
        second_num_strata_deposited,
        actual_rank_of_mrca
      ).template cast<HSTRAT_RANK_T>();
    } else return HAS_SCRY_OTHER{};
  }

  double CalcMrcaUncertaintyRelExact(
    const HSTRAT_RANK_T first_num_strata_deposited,
    const HSTRAT_RANK_T second_num_strata_deposited,
    const HSTRAT_RANK_T actual_rank_of_mrca
  ) const {
    if constexpr (HAS_SCRY_OTHER::value) {
      return policy_obj.attr("CalcMrcaUncertaintyRelExact")(
        first_num_strata_deposited,
        second_num_strata_deposited,
        actual_rank_of_mrca
      ).template cast<double>();
    } else return HAS_SCRY_OTHER{};
  }

  HSTRAT_RANK_T CalcNumStrataRetainedExact(
    const HSTRAT_RANK_T num_strata_deposited
  ) const {
    if constexpr (HAS_SCRY_OTHER::value) {
      return policy_obj.attr("CalcNumStrataRetainedExact")(
        num_strata_deposited
      ).template cast<HSTRAT_RANK_T>();
    } else return HAS_SCRY_OTHER{};
  }

  HSTRAT_RANK_T CalcRankAtColumnIndex(
    const HSTRAT_RANK_T index,
    const HSTRAT_RANK_T num_strata_deposited
  ) const {
    if constexpr (HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX::value) {
      return policy_obj.attr("CalcRankAtColumnIndex")(
        index,
        num_strata_deposited
      ).template cast<HSTRAT_RANK_T>();
    } else return HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX{};
  }

  cppcoro::generator<const HSTRAT_RANK_T> IterRetainedRanks(
    const HSTRAT_RANK_T num_strata_deposited
  ) const {
    if constexpr (HAS_SCRY_OTHER::value) {
      return std::move(shim_py_object_generator<const HSTRAT_RANK_T>(
        policy_obj.attr("IterRetainedRanks")(num_strata_deposited)
      ));
    } else return HAS_SCRY_OTHER{};
  }

};

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_PYBIND_PYOBJECTPOLICYSHIM_HPP_INCLUDE
