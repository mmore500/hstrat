// cppimport
#include <cstddef>
#include <type_traits>
#include <variant>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <hstrat/genome_instrumentation/HereditaryStratigraphicColumn.hpp>
#include <hstrat_pybind/all_tu_declarations.hpp>
#include <hstrat_pybind/callable.hpp>
#include <hstrat_pybind/pyobject.hpp>
#include <hstrat_pybind/PyObjectOrderedStoreShim.hpp>
#include <hstrat_pybind/PyObjectPolicyShim.hpp>
#include <hstrat/stratum_retention_strategy/stratum_retention_algorithms/fixed_resolution_algo/Policy.hpp>

namespace py = pybind11;
using namespace pybind11::literals;

#define INSTANCE(SELF_T) \
HereditaryStratigraphicColumnABC_register( \
py::class_<SELF_T>(\
  m,\
  "_HereditaryStratigraphicColumnNative"#SELF_T\
)\
.def("__eq__",\
  [](const SELF_T& self, const SELF_T& other){\
    return self == other;\
  }\
)\
.def("__eq__",\
  [](const SELF_T& self, py::object other){\
    return false;\
  }\
)\
.def("__copy__", [](const SELF_T& self){ return self; })\
.def("__deepcopy__", [](const SELF_T& self, py::object){\
  return self.Clone();\
})\
.def("DepositStratum", [](SELF_T& self){ self.DepositStratum(); })\
.def("DepositStratum", [](SELF_T& self, py::object annotation){\
  self.DepositStratum(annotation);\
}, py::arg("annotation"))\
.def("IterRetainedRanks",\
  &SELF_T::IterRetainedRanks, py::keep_alive<0, 1>()\
)\
.def("GetNumStrataRetained", &SELF_T::GetNumStrataRetained)\
.def("GetNumStrataDeposited", &SELF_T::GetNumStrataDeposited)\
.def("GetStratumAtColumnIndex", &SELF_T::GetStratumAtColumnIndex)\
.def("GetRankAtColumnIndex", &SELF_T::GetRankAtColumnIndex)\
.def("GetColumnIndexOfRank", &SELF_T::GetColumnIndexOfRank)\
.def("GetNumDiscardedStrata", &SELF_T::GetNumDiscardedStrata)\
.def(\
  "GetStratumDifferentiaBitWidth",\
  [](const SELF_T&){ return SELF_T::GetStratumDifferentiaBitWidth(); }\
)\
.def("HasDiscardedStrata", &SELF_T::HasDiscardedStrata)\
.def(\
  "CalcProbabilityDifferentiaCollision",\
  [](const SELF_T&){ return SELF_T::CalcProbabilityDifferentiaCollision(); }\
)\
.def(\
  "CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions",\
  &SELF_T::CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions,\
  py::arg("significance_level")\
)\
.def(\
  "Clone",\
  [](const SELF_T& self){ return self; }\
)\
.def("CloneDescendant", [](SELF_T& self){\
  return self.CloneDescendant();\
})\
.def("CloneDescendant", [](SELF_T& self, py::object annotation){\
  return self.CloneDescendant(annotation);\
}, py::arg("stratum_annotation"))\
.def_property_readonly(\
  "_stratum_ordered_store",\
  &SELF_T::_GetStratumOrderedStoreForPy\
)\
.def("_ShouldOmitStratumDepositionRank",\
  [](const SELF_T&){ return SELF_T::_omits_stratum_deposition_rank();}\
) \
)

using bit_nodeporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  bool, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using byte_nodeporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  uint8_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using word_nodeporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  uint16_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using doubleword_nodeporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  uint32_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using quadword_nodeporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  uint64_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using bit_deporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  bool, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using byte_deporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  uint8_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using word_deporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  uint16_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using doubleword_deporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  uint32_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using quadword_deporank_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  uint64_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject // ANNOTATION_T
>;

using bit_nodeporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  bool, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

using byte_nodeporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  uint8_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

using word_nodeporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  uint16_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

using doubleword_nodeporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  uint32_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

using quadword_nodeporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject // POLICY_SPEC
  >, // POLICY_T
  uint64_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

using bit_deporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  bool, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

using byte_deporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  uint8_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

using word_deporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  uint16_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

using doubleword_deporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  uint32_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

using quadword_deporank_shimstore_t = hstrat::HereditaryStratigraphicColumn<
  hstrat_pybind::PyObjectPolicyShim<
    hstrat_pybind::pyobject, // POLICY_SPEC
    std::false_type // HAS_SCRY_CALC_RANK_AT_COLUMN_INDEX
  >, // POLICY_T
  uint64_t, // DIFFERENTIA_T
  hstrat_pybind::pyobject, // ANNOTATION_T
  hstrat_pybind::PyObjectOrderedStoreShim // STORE_T
>;

PYBIND11_MODULE(_HereditaryStratigraphicColumnNative, m) {

  // ensure availability of algo::PolicySpec
  // see https://stackoverflow.com/questions/51833291/splitting-up-pybind11-modules-and-issues-with-automatic-type-conversion#comment113430868_51852400
  py::module::import("cppimport.import_hook");
  auto importlib = py::module::import("importlib");
  importlib.attr("import_module")(
    "...._bindings",
    m.attr("__name__")
  );
  importlib.attr("import_module")(
    "....stratum_retention_strategy.stratum_retention_algorithms.fixed_resolution_algo._Policy_._PolicyNative",
    m.attr("__name__")
  );
  importlib.attr("import_module")(
    "..._HereditaryStratum_._HereditaryStratumNative",
    m.attr("__name__")
  );
  importlib.attr("import_module")(
    "...stratum_ordered_stores._HereditaryStratumOrderedStoreList_._HereditaryStratumOrderedStoreListNative",
    m.attr("__name__")
  );

  m.def("HereditaryStratigraphicColumnNative", [](
    py::object stratum_retention_policy,
    const bool always_store_rank_in_stratum,
    const int stratum_differentia_bit_width,
    const py::object initial_stratum_annotation,
    const py::object stratum_ordered_store
  ) -> std::variant<
      bit_deporank_t, byte_deporank_t, word_deporank_t, doubleword_deporank_t, quadword_deporank_t,
      bit_nodeporank_t, byte_nodeporank_t, word_nodeporank_t, doubleword_nodeporank_t, quadword_nodeporank_t,
      bit_deporank_shimstore_t, byte_deporank_shimstore_t, word_deporank_shimstore_t, doubleword_deporank_shimstore_t, quadword_deporank_shimstore_t,
      bit_nodeporank_shimstore_t, byte_nodeporank_shimstore_t, word_nodeporank_shimstore_t, doubleword_nodeporank_shimstore_t, quadword_nodeporank_shimstore_t
    > {

      const bool has_calc_rank_at_column_index = stratum_retention_policy.attr(
        "HasCalcRankAtColumnIndex"
      )().template cast<bool>();

      if (
        stratum_differentia_bit_width == 1
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return bit_nodeporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 8
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return byte_nodeporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 16
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return word_nodeporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 32
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return doubleword_nodeporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 64
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return quadword_nodeporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 1
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return bit_deporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 8
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return byte_deporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 16
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return word_deporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 32
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return doubleword_deporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 64
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && stratum_ordered_store.is_none()
      ) {
        return quadword_deporank_t(
          stratum_retention_policy,
          initial_stratum_annotation
        );
      }
      else if (
        stratum_differentia_bit_width == 1
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return bit_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 8
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return byte_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 16
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return word_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 32
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return doubleword_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 64
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return quadword_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 1
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return bit_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 8
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return byte_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 16
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return word_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 32
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return doubleword_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 64
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && hstrat_pybind::callable(stratum_ordered_store)
      ) {
        return quadword_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          {stratum_ordered_store(), 0}
        );
      }
      else if (
        stratum_differentia_bit_width == 1
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = bit_nodeporank_shimstore_t::store_t;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return bit_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else if (
        stratum_differentia_bit_width == 8
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = byte_nodeporank_shimstore_t::store_t;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return byte_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else if (
        stratum_differentia_bit_width == 16
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = word_nodeporank_shimstore_t::store_t;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return word_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else if (
        stratum_differentia_bit_width == 32
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = doubleword_nodeporank_shimstore_t::store_t;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return doubleword_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else if (
        stratum_differentia_bit_width == 64
        && (!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = quadword_nodeporank_shimstore_t::store_t;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return quadword_nodeporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else if (
        stratum_differentia_bit_width == 1
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = bit_deporank_shimstore_t::store_t;;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return bit_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else if (
        stratum_differentia_bit_width == 8
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = byte_deporank_shimstore_t::store_t;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return byte_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else if (
        stratum_differentia_bit_width == 16
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = word_deporank_shimstore_t::store_t;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return word_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else if (
        stratum_differentia_bit_width == 32
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = doubleword_deporank_shimstore_t::store_t;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return doubleword_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else if (
        stratum_differentia_bit_width == 64
        && !(!always_store_rank_in_stratum && has_calc_rank_at_column_index)
        && py::isinstance<py::tuple>(stratum_ordered_store)
      ) {
        using shimstore_t = quadword_deporank_shimstore_t::store_t;
        const py::tuple as_tuple = stratum_ordered_store;
        const auto first = shimstore_t(as_tuple[0]);
        const auto second = as_tuple[1].cast<HSTRAT_RANK_T>();
        return quadword_deporank_shimstore_t(
          stratum_retention_policy,
          initial_stratum_annotation,
          std::tuple<shimstore_t, HSTRAT_RANK_T>{first, second}
        );
      }
      else throw std::invalid_argument{"unsupported differentia bit width"};
    },
    py::arg("stratum_retention_policy") = hstrat::fixed_resolution_algo::Policy<>{1},
    py::kw_only(),
    py::arg("always_store_rank_in_stratum") = false,
    py::arg("stratum_differentia_bit_width") = 64,
    py::arg("initial_stratum_annotation") =  py::none(),
    py::arg("stratum_ordered_store") = py::none()
  );

  const auto HereditaryStratigraphicColumnABC_register \
    = importlib.attr("import_module")(
        "..._detail",
        m.attr("__name__")
  ).attr("HereditaryStratigraphicColumnABC").attr("register");

  INSTANCE(bit_deporank_t);
  INSTANCE(byte_deporank_t);
  INSTANCE(word_deporank_t);
  INSTANCE(doubleword_deporank_t);
  INSTANCE(quadword_deporank_t);
  INSTANCE(bit_nodeporank_t);
  INSTANCE(byte_nodeporank_t);
  INSTANCE(word_nodeporank_t);
  INSTANCE(doubleword_nodeporank_t);
  INSTANCE(quadword_nodeporank_t);
  INSTANCE(bit_deporank_shimstore_t);
  INSTANCE(byte_deporank_shimstore_t);
  INSTANCE(word_deporank_shimstore_t);
  INSTANCE(doubleword_deporank_shimstore_t);
  INSTANCE(quadword_deporank_shimstore_t);
  INSTANCE(bit_nodeporank_shimstore_t);
  INSTANCE(byte_nodeporank_shimstore_t);
  INSTANCE(word_nodeporank_shimstore_t);
  INSTANCE(doubleword_nodeporank_shimstore_t);
  INSTANCE(quadword_nodeporank_shimstore_t);

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
cfg['include_dirs'] = [f'{root_dir}/include']

setup_pybind11(cfg)
%>
*/
