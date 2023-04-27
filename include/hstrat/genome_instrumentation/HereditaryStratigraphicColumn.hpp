#pragma once
#ifndef HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATIGRAPHICCOLUMN_HPP_INCLUDE
#define HSTRAT_GENOME_INSTRUMENTATION_HEREDITARYSTRATIGRAPHICCOLUMN_HPP_INCLUDE

#include <cassert>
#include <climits>
#include <cstddef>
#include <tuple>
#include <type_traits>
#include <utility>

#include "../../../third-party/ccmath/include/ccmath/ceil.hpp"
#include "../../../third-party/ccmath/include/ccmath/ldexp.hpp"
#include "../../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../../hstrat_auxlib/audit_cast.hpp"
#include "../../hstrat_auxlib/binary_search.hpp"
#include "../../hstrat_auxlib/constexpr_log.hpp"
#include "../../hstrat_auxlib/is_specialization_of.hpp"
#include "../../hstrat_auxlib/Monostate.hpp"
#include "../../hstrat_pybind/PyObjectOrderedStoreShimConcept.hpp"

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

  using deposition_rank_t = std::conditional_t<
    POLICY_T::has_calc_rank_at_column_index(),
    hstrat_auxlib::Monostate,
    HSTRAT_RANK_T
  >;

  using stratum_t_ = hstrat::HereditaryStratum<
    DIFFERENTIA_T,
    ANNOTATION_T,
    deposition_rank_t
  >;

  using store_t_ = STORE_T<stratum_t_>;

  POLICY_T policy;
  store_t_ store;
  HSTRAT_RANK_T num_strata_deposited;

public:

  using store_t = store_t_;
  using store_with_deposit_count_t = std::tuple<store_t, HSTRAT_RANK_T>;
  using stratum_t = stratum_t_;
  using differentia_t = typename stratum_t::differentia_t;
  using annotation_t = typename stratum_t::annotation_t;
  consteval bool has_annotation() {
    return std::is_same_v<annotation_t, hstrat_auxlib::Monostate>;
  }

  HereditaryStratigraphicColumn(
    const POLICY_T& stratum_retention_policy,
    const ANNOTATION_T& initial_annotation={},
    store_with_deposit_count_t store_and_deposit_count={}
  )
  : policy(stratum_retention_policy)
  , store(std::move(std::get<0>(store_and_deposit_count)))
  , num_strata_deposited(std::get<1>(store_and_deposit_count))
  {
    assert(GetNumStrataRetained() <= GetNumStrataDeposited());
    if (num_strata_deposited == 0) {
      DepositStratum(initial_annotation);
    }
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

  const store_t& GetStratumOrderedStore() const { return store; }

  decltype(auto) _GetStratumOrderedStoreForPy() const {
    if constexpr (hstrat_pybind::PyObjectOrderedStoreShimConcept<store_t>) {
      return GetStratumOrderedStore().GetObj();
    } else return GetStratumOrderedStore();
  }

  constexpr static bool _omits_stratum_deposition_rank() {
    return POLICY_T::has_calc_rank_at_column_index();
  }

private:

  void PurgeColumn() {
    if constexpr (_omits_stratum_deposition_rank()) {
      store.DelRanks(
        policy.GenDropRanks(num_strata_deposited, IterRetainedRanks()),
        [this](const HSTRAT_RANK_T rank){ return GetColumnIndexOfRank(rank); }
      );
    } else {
      store.DelRanks(
        policy.GenDropRanks(num_strata_deposited, IterRetainedRanks())
      );
    }
  }

  cppcoro::generator<const HSTRAT_RANK_T>
  IterRetainedRanksViaGetRankAtColumnIndex() const {
    for (std::size_t i{}; i < GetNumStrataRetained(); ++i) {
      co_yield GetRankAtColumnIndex(i);
    }
  }

public:

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

  cppcoro::generator<const HSTRAT_RANK_T> IterRetainedRanks() const {
    if constexpr (POLICY_T::has_iter_retained_ranks()) {
      return policy.IterRetainedRanks(GetNumStrataDeposited());
    } else if constexpr (_omits_stratum_deposition_rank()) {
      return IterRetainedRanksViaGetRankAtColumnIndex();
    } else {
      return store.IterRetainedRanks();
    }
  }

  HSTRAT_RANK_T GetNumStrataRetained() const {
    return store.GetNumStrataRetained();
  }

  HSTRAT_RANK_T GetNumStrataDeposited() const { return num_strata_deposited; }

  decltype(auto) GetStratumAtColumnIndex(
    const HSTRAT_RANK_T index
  ) const {
    if constexpr (_omits_stratum_deposition_rank()) {
      return store.GetStratumAtColumnIndex(
        index,
        [this](const HSTRAT_RANK_T rank){ return GetRankAtColumnIndex(rank); }
      );
    } else {
      return store.GetStratumAtColumnIndex(index);
    }
  }

  const HSTRAT_RANK_T GetRankAtColumnIndex(const HSTRAT_RANK_T index) const {
    if constexpr (_omits_stratum_deposition_rank()) {
      return policy.CalcRankAtColumnIndex(index, num_strata_deposited);
    } else {
      return store.GetRankAtColumnIndex(index);
    }
  }

  HSTRAT_RANK_T GetColumnIndexOfRank(const HSTRAT_RANK_T rank) const {
    if constexpr (_omits_stratum_deposition_rank()) {
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

  constexpr static int GetStratumDifferentiaBitWidth() {
    if constexpr (std::is_same_v<differentia_t, bool>) { return 1; }
    else return sizeof(differentia_t) * CHAR_BIT;
  }

  HSTRAT_RANK_T HasDiscardedStrata() const {
    return GetNumDiscardedStrata();
  }

  constexpr static double CalcProbabilityDifferentiaCollision() {
    return ccmath::ldexp(1, -GetStratumDifferentiaBitWidth());
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
