#pragma once
#ifndef HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATUM_HPP_INCLUDE
#define HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATUM_HPP_INCLUDE

#include <cstdint>
#include <optional>
#include <tuple>
#include <variant>

#include "../config/HSTRAT_RANK_T.hpp"
#include "../config/pick_differentia.hpp"

namespace hstrat {

template<
  typename DIFFERENTIA_T=uint64_t,
  typename ANNOTATION_T=std::monostate,
  typename DEPOSITION_RANK_T=std::monostate
>
class HereditaryStratum {

  [[no_unique_address]] DIFFERENTIA_T differentia;
  [[no_unique_address]] ANNOTATION_T annotation;
  [[no_unique_address]] DEPOSITION_RANK_T deposition_rank;

public:

  HereditaryStratum(
    HSTRAT_RANK_T deposition_rank,
    ANNOTATION_T annotation={}
  )
  : differentia(
    hstrat::pick_differentia<DIFFERENTIA_T>(deposition_rank)
  )
  , annotation(annotation)
  , deposition_rank(
    [&deposition_rank](){
      if constexpr (std::is_same_v<DEPOSITION_RANK_T, HSTRAT_RANK_T>) {
        return deposition_rank;
      } else return DEPOSITION_RANK_T{};
    }()
  )
  { }

  using with_deposition_rank_t = HereditaryStratum<
    DIFFERENTIA_T,
    ANNOTATION_T,
    HSTRAT_RANK_T
  >;
  using without_deposition_rank_t = HereditaryStratum<
    DIFFERENTIA_T,
    ANNOTATION_T,
    std::monostate
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

  ANNOTATION_T GetAnnotation() const { return annotation; }

  DIFFERENTIA_T GetDifferentia() const { return differentia; }

};

} // namespace hstrat

#endif // #ifndef HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATUM_HPP_INCLUDE
