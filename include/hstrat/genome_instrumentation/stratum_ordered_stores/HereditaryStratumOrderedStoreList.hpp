#pragma once
#ifndef HSTRAT_GENOME_INSTRUMENTATION_STRATUM_ORDERED_STORES_HEREDITARYSTRATUMORDEREDSTORELIST_HPP_INCLUDE
#define HSTRAT_GENOME_INSTRUMENTATION_STRATUM_ORDERED_STORES_HEREDITARYSTRATUMORDEREDSTORELIST_HPP_INCLUDE

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <functional>
#include <iterator>
#include <ranges>
#include <type_traits>
#include <utility>
#include <vector>

#include "../../../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../../../hstrat_auxlib/audit_cast.hpp"
#include "../../../hstrat_auxlib/binary_search.hpp"
#include "../../../hstrat_auxlib/deepcopy.hpp"
#include "../../../hstrat_auxlib/HSTRAT_UNUSED.hpp"
#include "../../../hstrat_auxlib/Monostate.hpp"

#include "../../config/HSTRAT_RANK_T.hpp"

#include "../HereditaryStratum.hpp"

namespace hstrat {

template<typename HEREDITARY_STRATUM_T>
class HereditaryStratumOrderedStoreList {

  // strata stored from most ancient (index 0, front) to most recent (back)
  std::vector<HEREDITARY_STRATUM_T> data;

public:

  using hereditary_stratum_t = HEREDITARY_STRATUM_T;

  HereditaryStratumOrderedStoreList Clone() const {
    auto res = *this;
    std::transform(
      std::begin(res.data), std::end(res.data), std::begin(res.data),
      hstrat_auxlib::deepcopy<HEREDITARY_STRATUM_T>
    );
    return res;
  }

  bool operator==(const HereditaryStratumOrderedStoreList& other) const {
    return data == other.data;
  }

  void DepositStratum(
    const HSTRAT_RANK_T,
    const HEREDITARY_STRATUM_T& stratum
  ) { data.push_back(stratum); }

  void DepositStratum(
    const HSTRAT_RANK_T,
    HEREDITARY_STRATUM_T&& stratum
  ) { data.push_back(std::move(stratum)); }

  HSTRAT_RANK_T GetNumStrataRetained() const {
    return hstrat_auxlib::audit_cast<HSTRAT_RANK_T>(data.size());
  }

  template<typename F=hstrat_auxlib::Monostate>
  const HEREDITARY_STRATUM_T& GetStratumAtColumnIndex(
    const HSTRAT_RANK_T index,
    F={} // get_rank_at_column_index, unused
  ) const {
    return data[index];
  }

  HSTRAT_RANK_T GetRankAtColumnIndex(
    const hstrat::RankTConcept auto index
  ) const {
    return GetStratumAtColumnIndex(index).GetDepositionRank();
  }

  // returns min(rank + 1, GetNumStrataRetained()) on failure
  HSTRAT_RANK_T GetColumnIndexOfRank(
    const hstrat::RankTConcept auto rank
  ) const {
    const std::size_t ub = std::min(rank + 1, GetNumStrataRetained());
    const auto res = hstrat_auxlib::audit_cast<HSTRAT_RANK_T>(
      hstrat_auxlib::binary_search(
        [this, rank](const std::size_t idx){
          return GetRankAtColumnIndex(
            hstrat_auxlib::audit_cast<HSTRAT_RANK_T>(idx)
          ) >= rank;
        },
        ub
      )
    );
    return (GetRankAtColumnIndex(res) == rank) ? res : ub;
  }

  template<typename F=hstrat_auxlib::Monostate>
  void DelRanks(
    cppcoro::generator<const HSTRAT_RANK_T> ranks,
    // deposition ranks might not be stored in strata
    F get_column_index_of_rank={}
  ) {
    std::vector<HSTRAT_RANK_T> indices;
    std::ranges::transform(
      ranks,
      std::back_inserter(indices),
      [this, &get_column_index_of_rank](const HSTRAT_RANK_T rank) {
        if constexpr (std::is_same_v<F, hstrat_auxlib::Monostate>) {
          HSTRAT_UNUSED(get_column_index_of_rank);
          return GetColumnIndexOfRank(rank);
        } else {
          HSTRAT_UNUSED(this);
          return get_column_index_of_rank(rank);
        }
      }
    );

    assert(
      // vector should be sorted in ascending order
      std::end(indices) == std::adjacent_find(
        std::begin(indices),
        std::end(indices),
        std::greater<HSTRAT_RANK_T>{}
      )
    );

    // delete in reverse order to prevent invalidation
    std::for_each(
      std::rbegin(indices),
      std::rend(indices),
      [this](const HSTRAT_RANK_T index){
        data.erase( std::next(std::begin(data), index) );
      }
    );
  }

    cppcoro::generator<const HSTRAT_RANK_T> IterRetainedRanks() const {
      // must make copy to prevent invalidation when strata are deleted
      // note, however, that copy is made lazily
      // (only when first item requested)
      std::vector<HSTRAT_RANK_T> ranks;
      ranks.reserve(data.size());
      std::transform(
        std::begin(data),
        std::end(data),
        std::back_inserter(ranks),
        [](const HEREDITARY_STRATUM_T& stratum) {
          return stratum.GetDepositionRank();
        }
      );

      for (const HSTRAT_RANK_T rank : ranks) co_yield rank;
    }

    cppcoro::generator<HEREDITARY_STRATUM_T> IterRetainedStrata() const {
      for (auto stratum : data) co_yield stratum;
    }

    template<typename F=hstrat_auxlib::Monostate>
    cppcoro::generator<
      std::tuple<HSTRAT_RANK_T, typename HEREDITARY_STRATUM_T::differentia_t>
    > IterRankDifferentiaZip(
      // deposition ranks might not be stored in strata
      const HSTRAT_RANK_T start_column_index = 0,
      F get_rank_at_column_index = {}
    ) const {
      for (
        HSTRAT_RANK_T index{start_column_index};
        index < GetNumStrataRetained();
        ++index
      ) {
        const HSTRAT_RANK_T rank = [this, &get_rank_at_column_index, index](){
          if constexpr (std::is_same_v<F, hstrat_auxlib::Monostate>) {
            HSTRAT_UNUSED(get_rank_at_column_index);
            return GetRankAtColumnIndex(index);
          } else {
            HSTRAT_UNUSED(this);
            return get_rank_at_column_index(index);
          }
        }();
        const auto& stratum = data[index];
        co_yield std::tuple{
          rank,
          stratum.GetDifferentia()
        };
      }
    }

};

} // namespace hstrat

#endif // #ifndef HSTRAT_GENOME_INSTRUMENTATION_STRATUM_ORDERED_STORES_HEREDITARYSTRATUMORDEREDSTORELIST_HPP_INCLUDE
