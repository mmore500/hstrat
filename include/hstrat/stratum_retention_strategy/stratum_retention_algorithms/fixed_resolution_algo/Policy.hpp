#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICY_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICY_HPP_INCLUDE

#include <utility>

#include "PolicySpecDynamic.hpp"

#include "enact/GenDropRanksFtor.hpp"
#include "invar/CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankFtor.hpp"
#include "invar/CalcMrcaUncertaintyAbsUpperBoundFtor.hpp"
#include "invar/CalcMrcaUncertaintyAbsUpperBoundPessimalRankFtor.hpp"
#include "invar/CalcMrcaUncertaintyRelUpperBoundAtPessimalRankFtor.hpp"
#include "invar/CalcMrcaUncertaintyRelUpperBoundPessimalRankFtor.hpp"
#include "invar/CalcNumStrataRetainedUpperBoundFtor.hpp"
#include "scry/CalcMrcaUncertaintyAbsExactFtor.hpp"
#include "scry/CalcMrcaUncertaintyRelExactFtor.hpp"
#include "scry/CalcNumStrataRetainedExactFtor.hpp"
#include "scry/CalcRankAtColumnIndexFtor.hpp"
#include "scry/IterRetainedRanksFtor.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

template <typename POLICY_SPEC> class Policy {

  [[no_unique_address]] POLICY_SPEC spec;

public:
  // enactment
  [[no_unique_address]] GenDropRanksFtor GenDropRanks;

  // invariants
  [[no_unique_address]] CalcMrcaUncertaintyAbsUpperBoundFtor<POLICY_SPEC>
      CalcMrcaUncertaintyAbsUpperBound;
  [[no_unique_address]] CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankFtor<
      POLICY_SPEC>
      CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank;
  [[no_unique_address]] CalcMrcaUncertaintyAbsUpperBoundPessimalRankFtor<
      POLICY_SPEC>
      CalcMrcaUncertaintyAbsUpperBoundPessimalRank;
  [[no_unique_address]] CalcMrcaUncertaintyRelUpperBoundAtPessimalRankFtor<
      POLICY_SPEC>
      CalcMrcaUncertaintyRelUpperBoundAtPessimalRank;
  [[no_unique_address]] CalcMrcaUncertaintyRelUpperBoundPessimalRankFtor<
      POLICY_SPEC>
      CalcMrcaUncertaintyRelUpperBoundPessimalRank;
  [[no_unique_address]] CalcNumStrataRetainedUpperBoundFtor<POLICY_SPEC>
      CalcNumStrataRetainedUpperBound;

  // scrying
  [[no_unique_address]] CalcMrcaUncertaintyAbsExactFtor<POLICY_SPEC>
      CalcMrcaUncertaintyAbsExact;
  [[no_unique_address]] CalcMrcaUncertaintyRelExactFtor<POLICY_SPEC>
      CalcMrcaUncertaintyRelExact;
  [[no_unique_address]] CalcNumStrataRetainedExactFtor<POLICY_SPEC>
      CalcNumStrataRetainedExact;
  [[no_unique_address]] CalcRankAtColumnIndexFtor<POLICY_SPEC>
      CalcRankAtColumnIndex;
  [[no_unique_address]] IterRetainedRanksFtor<POLICY_SPEC> IterRetainedRanks;

  template <typename... Args>
  Policy(Args &&... args)
      : spec(std::forward<Args>(args)...), GenDropRanks(spec),
        CalcMrcaUncertaintyAbsUpperBound(spec),
        CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(spec),
        CalcMrcaUncertaintyAbsUpperBoundPessimalRank(spec),
        CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(spec),
        CalcMrcaUncertaintyRelUpperBoundPessimalRank(spec),
        CalcNumStrataRetainedUpperBound(spec),
        CalcMrcaUncertaintyAbsExact(spec), CalcMrcaUncertaintyRelExact(spec),
        CalcNumStrataRetainedExact(spec), CalcRankAtColumnIndex(spec),
        IterRetainedRanks(spec) {}
};

} // namespace fixed_resolution_algo
} // namespace hstrat

using PolicyDynamic = Policy<hstrat::fixed_resolution_algo::PolicySpecDynamic>;

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICY_HPP_INCLUDE
