#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DETAIL_POLICYCOUPLER_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DETAIL_POLICYCOUPLER_HPP_INCLUDE

#include <tuple>
#include <utility>

#include "../../../../../third-party/fmt/include/fmt/core.h"

#include "Monostate.hpp"

namespace hstrat {
namespace detail {

template<
  typename POLICY_SPEC,
  // enactment
  typename GEN_DROP_RANKS_FTOR,
  // invariants
  typename CALC_MRCA_UNCERTAINTY_ABS_UPPER_BOUND_AT_PESSIMAL_RANK_FTOR,
  typename CALC_MRCA_UNCERTAINTY_ABS_UPPER_BOUND_FTOR,
  typename CALC_MRCA_UNCERTAINTY_ABS_UPPER_BOUND_PESSIMAL_RANK_FTOR,
  typename CALC_MRCA_UNCERTAINTY_REL_UPPER_BOUND_AT_PESSIMAL_RANK_FTOR,
  typename CALC_MRCA_UNCERTAINTY_REL_UPPER_BOUND_FTOR,
  typename CALC_MRCA_UNCERTAINTY_REL_UPPER_BOUND_PESSIMAL_RANK_FTOR,
  typename CALC_NUM_STRATA_RETAINED_UPPER_BOUND_FTOR,
  // scrying
  typename CALC_MRCA_UNCERTAINTY_ABS_EXACT_FTOR,
  typename CALC_MRCA_UNCERTAINTY_REL_EXACT_FTOR,
  typename CALC_NUM_STRATA_RETAINED_EXACT_FTOR,
  typename CALC_RANK_AT_COLUMN_INDEX_FTOR,
  typename ITER_RETAINED_RANKS_FTOR
>
class PolicyCoupler {

  [[no_unique_address]] POLICY_SPEC spec;

  // enactment
  [[no_unique_address]] GEN_DROP_RANKS_FTOR gen_drop_ranks_ftor;

  // invariants
  [[no_unique_address]]
      CALC_MRCA_UNCERTAINTY_ABS_UPPER_BOUND_AT_PESSIMAL_RANK_FTOR
      calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor;
  [[no_unique_address]]
    CALC_MRCA_UNCERTAINTY_ABS_UPPER_BOUND_FTOR
    calc_mrca_uncertainty_abs_upper_bound_ftor;
  [[no_unique_address]]
    CALC_MRCA_UNCERTAINTY_ABS_UPPER_BOUND_PESSIMAL_RANK_FTOR
    calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor;
  [[no_unique_address]]
    CALC_MRCA_UNCERTAINTY_REL_UPPER_BOUND_AT_PESSIMAL_RANK_FTOR
    calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor;
  [[no_unique_address]]
    CALC_MRCA_UNCERTAINTY_REL_UPPER_BOUND_FTOR
    calc_mrca_uncertainty_rel_upper_bound_ftor;
  [[no_unique_address]]
    CALC_MRCA_UNCERTAINTY_REL_UPPER_BOUND_PESSIMAL_RANK_FTOR
    calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor;
  [[no_unique_address]] CALC_NUM_STRATA_RETAINED_UPPER_BOUND_FTOR
    calc_num_strata_retained_upper_bound_ftor;

  // scrying
  [[no_unique_address]] CALC_MRCA_UNCERTAINTY_ABS_EXACT_FTOR
    calc_mrca_uncertainty_abs_exact_ftor;
  [[no_unique_address]] CALC_MRCA_UNCERTAINTY_REL_EXACT_FTOR
    calc_mrca_uncertainty_rel_exact_ftor;
  [[no_unique_address]] CALC_NUM_STRATA_RETAINED_EXACT_FTOR
    calc_num_strata_retained_exact_ftor;
  [[no_unique_address]] CALC_RANK_AT_COLUMN_INDEX_FTOR
      calc_rank_at_column_index_ftor;
  [[no_unique_address]] ITER_RETAINED_RANKS_FTOR iter_retained_ranks_ftor;

public:

  using spec_t = POLICY_SPEC;

  consteval static bool has_calc_rank_at_column_index() {
    return !std::is_same_v<
      CALC_RANK_AT_COLUMN_INDEX_FTOR, hstrat::detail::Monostate
      >;
  }

  consteval static bool has_iter_retained_ranks() {
    return !std::is_same_v<
      ITER_RETAINED_RANKS_FTOR, hstrat::detail::Monostate
    >;
  }

  template <typename... Args>
  PolicyCoupler(Args &&... args)
    : spec(std::forward<Args>(args)...)
      // enactment
    , gen_drop_ranks_ftor(spec)
      // invariants
    , calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor(spec)
    , calc_mrca_uncertainty_abs_upper_bound_ftor(spec)
    , calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor(spec)
    , calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor(spec)
    , calc_mrca_uncertainty_rel_upper_bound_ftor(spec)
    , calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor(spec)
    , calc_num_strata_retained_upper_bound_ftor(spec)
      // scrying
    , calc_mrca_uncertainty_abs_exact_ftor(spec)
    , calc_mrca_uncertainty_rel_exact_ftor(spec)
    , calc_num_strata_retained_exact_ftor(spec)
    , calc_rank_at_column_index_ftor(spec)
    , iter_retained_ranks_ftor(spec)
  { }

  constexpr bool operator==(const PolicyCoupler& other) const {
    return std::tuple{
      spec//,
      // gen_drop_ranks_ftor,
      // calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor,
      // calc_mrca_uncertainty_abs_upper_bound_ftor,
      // calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor,
      // calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor,
      // calc_mrca_uncertainty_rel_upper_bound_ftor,
      // calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor,
      // calc_num_strata_retained_upper_bound_ftor,
      // calc_mrca_uncertainty_abs_exact_ftor,
      // calc_mrca_uncertainty_rel_exact_ftor,
      // calc_num_strata_retained_exact_ftor,
      // calc_rank_at_column_index_ftor,
      // iter_retained_ranks_ftor
    } == std::tuple{
      other.spec//,
      // other.gen_drop_ranks_ftor,
      // other.calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor,
      // other.calc_mrca_uncertainty_abs_upper_bound_ftor,
      // other.calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor,
      // other.calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor,
      // other.calc_mrca_uncertainty_rel_upper_bound_ftor,
      // other.calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor,
      // other.calc_num_strata_retained_upper_bound_ftor,
      // other.calc_mrca_uncertainty_abs_exact_ftor,
      // other.calc_mrca_uncertainty_rel_exact_ftor,
      // other.calc_num_strata_retained_exact_ftor,
      // other.calc_rank_at_column_index_ftor,
      // other.iter_retained_ranks_ftor
    };
  }

  const spec_t& GetSpec() const { return spec; }

  using without_calc_rank_at_column_index_t = hstrat::detail::PolicyCoupler<
    POLICY_SPEC,
    // enactment
    GEN_DROP_RANKS_FTOR,
    // invariants
    CALC_MRCA_UNCERTAINTY_ABS_UPPER_BOUND_AT_PESSIMAL_RANK_FTOR,
    CALC_MRCA_UNCERTAINTY_ABS_UPPER_BOUND_FTOR,
    CALC_MRCA_UNCERTAINTY_ABS_UPPER_BOUND_PESSIMAL_RANK_FTOR,
    CALC_MRCA_UNCERTAINTY_REL_UPPER_BOUND_AT_PESSIMAL_RANK_FTOR,
    CALC_MRCA_UNCERTAINTY_REL_UPPER_BOUND_FTOR,
    CALC_MRCA_UNCERTAINTY_REL_UPPER_BOUND_PESSIMAL_RANK_FTOR,
    CALC_NUM_STRATA_RETAINED_UPPER_BOUND_FTOR,
    // scrying
    CALC_MRCA_UNCERTAINTY_ABS_EXACT_FTOR,
    CALC_MRCA_UNCERTAINTY_REL_EXACT_FTOR,
    CALC_NUM_STRATA_RETAINED_EXACT_FTOR,
    hstrat::detail::Monostate,
    ITER_RETAINED_RANKS_FTOR
  >;

  const auto WithoutCalcRankAtColumnIndex() const {
    return without_calc_rank_at_column_index_t{spec};
  }

  std::string Repr() const {
    return fmt::format(
      "{}._Policy_.Policy(policy_spec={})",
      spec.GetAlgoIdentifier(),
      spec.Repr()
    );
  }

  std::string Str() const { return spec.Str(); }

  // enactment
  template <typename... Args>
  decltype(auto) GenDropRanks(Args &&... args) const {
    return gen_drop_ranks_ftor(*this, std::forward<Args>(args)...);
  }

  // invariants
  template <typename... Args>
  decltype(auto) CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
    Args &&... args
  ) const {
    return calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) CalcMrcaUncertaintyAbsUpperBound(Args &&... args) const {
    return calc_mrca_uncertainty_abs_upper_bound_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
    Args &&... args
  ) const {
    return calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
    Args &&... args
  ) const {
    return calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) CalcMrcaUncertaintyRelUpperBound(Args &&... args) const {
    return calc_mrca_uncertainty_rel_upper_bound_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) CalcMrcaUncertaintyRelUpperBoundPessimalRank(
    Args &&... args
  ) const {
    return calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) CalcNumStrataRetainedUpperBound(
    Args &&... args
  ) const {
    return calc_num_strata_retained_upper_bound_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  // scrying
  template <typename... Args>
  decltype(auto) CalcMrcaUncertaintyAbsExact(
    Args &&... args
  ) const {
    return calc_mrca_uncertainty_abs_exact_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) CalcMrcaUncertaintyRelExact(
    Args &&... args
  ) const {
    return calc_mrca_uncertainty_rel_exact_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) CalcNumStrataRetainedExact(
    Args &&... args
  ) const {
    return calc_num_strata_retained_exact_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) CalcRankAtColumnIndex(
    Args &&... args
  ) const {
    return calc_rank_at_column_index_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

  template <typename... Args>
  decltype(auto) IterRetainedRanks(
    Args &&... args
  ) const {
    return iter_retained_ranks_ftor(
      *this,
      std::forward<Args>(args)...
    );
  }

};

} // namespace detail
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_DETAIL_POLICYCOUPLER_HPP_INCLUDE