#pragma once
#ifndef HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATIGRAPHICCOLUMN_HPP_INCLUDE
#define HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATIGRAPHICCOLUMN_HPP_INCLUDE

#include <assert.h>
#include <climits>
#include <cstddef>
#include <tuple>
#include <type_traits>

#include "../../../third-party/ccmath/include/ccmath/ceil.hpp"
#include "../../../third-party/ccmath/include/ccmath/ldexp.hpp"
#include "../../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../../hstrat_auxlib/audit_cast.hpp"
#include "../../hstrat_auxlib/binary_search.hpp"
#include "../../hstrat_auxlib/constexpr_log.hpp"
#include "../../hstrat_auxlib/Monostate.hpp"

#include "../config/HSTRAT_RANK_T.hpp"

#include "HereditaryStratum.hpp"
#include "stratum_ordered_stores/HereditaryStratumOrderedStoreList.hpp"

namespace hstrat {

template<
  typename POLICY_T,
  typename DIFFERENTIA_T=uint64_t,
  typename ANNOTATION_T=hstrat_auxlib::Monostate,
  template<typename> typename STORE_T=hstrat::HereditaryStratumOrderedStoreList
>
class HereditaryStratigraphicColumn {

  using deposition_rank_t = std::conditional<
    POLICY_T::has_calc_rank_at_column_index(),
    HSTRAT_RANK_T,
    hstrat_auxlib::Monostate
  >;

  using stratum_t_ = hstrat::HereditaryStratum<
    DIFFERENTIA_T,
    ANNOTATION_T,
    deposition_rank_t
  >;

  POLICY_T policy;
  STORE_T<stratum_t_> store;
  HSTRAT_RANK_T num_strata_deposited{};

public:

  using stratum_t = stratum_t_;
  using differentia_t = stratum_t::differentia_t;
  using annotation_t = stratum_t::annotation_t;
  consteval bool has_annotation() { return std::is_same_v<annotation_t>; }

  HereditaryStratigraphicColumn(
    const POLICY_T& stratum_retention_policy,
    const ANNOTATION_T& initial_annotation={}
  ) : policy(stratum_retention_policy) {
    DepositStratum(initial_annotation);
  }

  bool operator==(const HereditaryStratigraphicColumn& other) const {
    return std::tuple{
      policy,
      store,
      num_strata_deposited
    } == std::tuple{
      other.policy,
      other.store,
      other.num_strata_deposited
    };
  }

private:

  consteval bool OmitsStratumDepositionRank() {
    return !POLICY_T::has_calc_rank_at_column_index();
  }

  void DepositStratum(const ANNOTATION_T& annotation={}) {
    const stratum_t stratum{
      num_strata_deposited,
      annotation
    };

    store.DepositStratum(
      num_strata_deposited,
      stratum
    );
    PurgeColumn();
    ++num_strata_deposited;

  }

  void PurgeColumn() {
    auto condemned_ranks = policy.GenDropRanks(num_strata_deposited);
    store.DelRanks(condemned_ranks);
  }

public:

  cppcoro::generator<const HSTRAT_RANK_T> IterRetainedRanks() const {
    if constexpr (POLICY_T::has_iter_retained_ranks()) {
      return policy.IterRetainedRanks(GetNumStrataDeposited());
    } else if constexpr (OmitsStratumDepositionRank()) {
      for (std::size_t i{}; i < GetNumStrataRetained(); ++i) {
        co_yield GetRankAtColumnIndex(i);
      }
    } else {
      return store.IterRetainedRanks();
    }
  }

  HSTRAT_RANK_T GetNumStrataRetained() const {
    return store.GetNumStrataRetained();
  }

  HSTRAT_RANK_T GetNumStrataDeposited() const { return num_strata_deposited; }

  const stratum_t& GetStratumAtColumnIndex(
    const HSTRAT_RANK_T index
  ) const {
    if constexpr (OmitsStratumDepositionRank()) {
      return store.GetStratumAtColumnIndex(
        index,
        [this](const HSTRAT_RANK_T rank){ return GetRankAtColumnIndex(rank); }
      );
    } else {
      return store.GetStratumAtColumnIndex(index);
    }
  }

  const HSTRAT_RANK_T GetRankAtColumnIndex(const HSTRAT_RANK_T index) const {
    if constexpr (OmitsStratumDepositionRank()) {
      return policy.CalcRankAtColumnIndex(index, num_strata_deposited);
    } else {
      return store.GetRankAtColumnIndex(index);
    }
  }

  HSTRAT_RANK_T GetColumnIndexOfRank(const HSTRAT_RANK_T rank) const {
    if constexpr (OmitsStratumDepositionRank()) {
      assert(GetNumStrataRetained());

      const std::size_t res = hstrat_auxlib::binary_search(
        [this, rank](const std::size_t index){
          return GetRankAtColumnIndex(index) >= rank;
        },
        GetNumStrataRetained() - 1
      );
      return hstrat_auxlib::audit_cast<HSTRAT_RANK_T>(res);
    } else {
      return store.GetColumnIndexOfRank(rank);
    }
  }

  HSTRAT_RANK_T GetNumDiscardedStrata() const {
    return GetNumStrataDeposited() - GetNumStrataRetained();
  }

  consteval int GetStratumDifferentiaBitWidth() {
    return hstrat_auxlib::audit_cast<int>(sizeof(differentia_t) * CHAR_BIT);
  }

  HSTRAT_RANK_T HasDiscardedStrata() const {
    return GetNumDiscardedStrata();
  }

  consteval double CalcProbabilityDifferentiaCollision() const {
    return ccmath::ldexp(-GetStratumDifferentiaBitWidth());
  }

  constexpr std::size_t
  CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
    const double significance_level
  ) const {
    assert(0.0 <= significance_level);
    assert(significance_level <= 1.0);
    constexpr double log_base = CalcProbabilityDifferentiaCollision();
    // log_b(a) = log(a) / log(b)
    const double log_numerator = hstrat_auxlib::constexpr_log(
      significance_level
    );
    constexpr double log_denominator = hstrat_auxlib::constexpr_log(log_base);
    const double log_result = log_numerator / log_denominator;

    const std::size_t rounded_up = hstrat_auxlib::audit_cast<std::size_t>(
      ccmath::ceil(log_result)
    );
    return rounded_up;
  }

  HereditaryStratigraphicColumn CloneDescendant(
    const ANNOTATION_T& annotation={}
  ) const {
    HereditaryStratigraphicColumn res{ *this };
    res.DepositStratum(annotation);
    return res;
  }

};

} // namespace hstrat

#endif // #ifndef HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATIGRAPHICCOLUMN_HPP_INCLUDE
