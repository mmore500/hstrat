#pragma once
#ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICY_HPP_INCLUDE
#define HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICY_HPP_INCLUDE

#include "../detail/PolicyCoupler.hpp"

#include "PolicySpec.hpp"

#include "enact/GenDropRanksFtor.hpp"
#include "invar/CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankFtor.hpp"
#include "invar/CalcMrcaUncertaintyAbsUpperBoundFtor.hpp"
#include "invar/CalcMrcaUncertaintyAbsUpperBoundPessimalRankFtor.hpp"
#include "invar/CalcMrcaUncertaintyRelUpperBoundAtPessimalRankFtor.hpp"
#include "invar/CalcMrcaUncertaintyRelUpperBoundFtor.hpp"
#include "invar/CalcMrcaUncertaintyRelUpperBoundPessimalRankFtor.hpp"
#include "invar/CalcNumStrataRetainedUpperBoundFtor.hpp"
#include "scry/CalcMrcaUncertaintyAbsExactFtor.hpp"
#include "scry/CalcMrcaUncertaintyRelExactFtor.hpp"
#include "scry/CalcNumStrataRetainedExactFtor.hpp"
#include "scry/CalcRankAtColumnIndexFtor.hpp"
#include "scry/IterRetainedRanksFtor.hpp"

namespace hstrat {
namespace fixed_resolution_algo {

template <
  typename POLICY_SPEC=hstrat::fixed_resolution_algo::PolicySpec
>
using = PolicyCoupler<
  POLICY_SPEC,
  GenDropRanksFtor,
  CalcMrcaUncertaintyAbsUpperBoundFtor,
  CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankFtor,
  CalcMrcaUncertaintyAbsUpperBoundFtor,
  CalcMrcaUncertaintyAbsUpperBoundPessimalRankFtor,
  CalcMrcaUncertaintyRelUpperBoundAtPessimalRankFtor,
  CalcMrcaUncertaintyRelUpperBoundPessimalRankFtor,
  CalcNumStrataRetainedUpperBoundFtor,
  CalcMrcaUncertaintyAbsExactFtor,
  CalcMrcaUncertaintyRelExactFtor,
  CalcNumStrataRetainedExactFtor,
  CalcRankAtColumnIndexFtor,
  IterRetainedRanksFtor,
>;

} // namespace fixed_resolution_algo
} // namespace hstrat

#endif // #ifndef HSTRAT_STRATUM_RETENTION_STRATEGY_STRATUM_RETENTION_ALGORITHMS_FIXED_RESOLUTION_ALGO_POLICY_HPP_INCLUDE
