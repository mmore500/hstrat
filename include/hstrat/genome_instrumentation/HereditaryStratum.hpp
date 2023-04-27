#pragma once
#ifndef HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATUM_HPP_INCLUDE
#define HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATUM_HPP_INCLUDE

#include <cstdint>
#include <optional>
#include <tuple>
#include <variant>

#include "../../hstrat_auxlib/HSTRAT_UNUSED.hpp"
#include "../../hstrat_auxlib/Monostate.hpp"
#include "../../hstrat_pybind/pybind11_or_stubs.hpp"
#include "../../hstrat_pybind/PyObjectConcept.hpp"

#include "../config/HSTRAT_RANK_T.hpp"
#include "../config/pick_differentia.hpp"

namespace py = pybind11;

namespace hstrat {

template<
  typename DIFFERENTIA_T=uint64_t,
  typename ANNOTATION_T=hstrat_auxlib::Monostate,
  typename DEPOSITION_RANK_T=hstrat_auxlib::Monostate
>
class HereditaryStratum {

  [[no_unique_address]] DIFFERENTIA_T differentia;
  [[no_unique_address]] ANNOTATION_T annotation;
  [[no_unique_address]] DEPOSITION_RANK_T deposition_rank;

public:

  HereditaryStratum(
    HSTRAT_RANK_T deposition_rank,
    ANNOTATION_T annotation,
    DIFFERENTIA_T differentia
  )
  : differentia(differentia)
  , annotation(annotation)
  , deposition_rank(
    [&deposition_rank](){
      if constexpr (std::is_same_v<DEPOSITION_RANK_T, HSTRAT_RANK_T>) {
        return deposition_rank;
      } else {
        HSTRAT_UNUSED(deposition_rank);
        return DEPOSITION_RANK_T{};
      }
    }()
  )
  { }

  HereditaryStratum(
    HSTRAT_RANK_T deposition_rank={},
    ANNOTATION_T annotation={}
  ) : HereditaryStratum(
    deposition_rank,
    annotation,
    hstrat::pick_differentia<DIFFERENTIA_T>(deposition_rank)
  )
  { }

  // non-template necessary for implicit conversion
  HereditaryStratum(py::object stratum)
  : differentia(
    stratum.attr("GetDifferentia")().template cast<DIFFERENTIA_T>()
  )
  , annotation(
    stratum.attr("GetAnnotation")()
  )
  , deposition_rank(
    [&stratum](){
      if constexpr (std::is_same_v<DEPOSITION_RANK_T, HSTRAT_RANK_T>) {
        const auto res = stratum.attr("GetDepositionRank")();
        if (res.is_none()) return HSTRAT_RANK_T{};
        else return res.template cast<HSTRAT_RANK_T>();
      } else {
        HSTRAT_UNUSED(stratum);
        return DEPOSITION_RANK_T{};
      }
    }()
  )
  { }

  using differentia_t = DIFFERENTIA_T;
  using annotation_t = ANNOTATION_T;
  using deposition_rank_t = DEPOSITION_RANK_T;

  using with_deposition_rank_t = HereditaryStratum<
    DIFFERENTIA_T,
    ANNOTATION_T,
    HSTRAT_RANK_T
  >;
  using without_deposition_rank_t = HereditaryStratum<
    DIFFERENTIA_T,
    ANNOTATION_T,
    hstrat_auxlib::Monostate
  >;

  bool operator==(const HereditaryStratum& other) const {
    return std::tuple{
      differentia,
      annotation,
      deposition_rank
    } == std::tuple{
      other.differentia,
      other.annotation,
      other.deposition_rank
    };
  }

  DEPOSITION_RANK_T GetDepositionRank() const { return deposition_rank; }

  const ANNOTATION_T& GetAnnotation() const { return annotation; }

  DIFFERENTIA_T GetDifferentia() const { return differentia; }

};

} // namespace hstrat

#endif // #ifndef HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATUM_HPP_INCLUDE
