#pragma once
#ifndef HSTRAT_PYBIND_PYOBJECTORDEREDSTORESHIM_HPP_INCLUDE
#define HSTRAT_PYBIND_PYOBJECTORDEREDSTORESHIM_HPP_INCLUDE

#include <functional>
#include <utility>

#include <pybind11/functional.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

#include "../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../hstrat_auxlib/Monostate.hpp"
#include "../hstrat/config/HSTRAT_RANK_T.hpp"
#include "../hstrat/genome_instrumentation/HereditaryStratum.hpp"

#include "shim_py_object_generator.hpp"

namespace hstrat_pybind {

template<typename HEREDITARY_STRATUM_T>
class PyObjectOrderedStoreShim {

  py::object store_obj;

public:

  using hereditary_stratum_t = HEREDITARY_STRATUM_T;

  PyObjectOrderedStoreShim(py::object obj) : store_obj(obj) {}

  bool operator==(const PyObjectOrderedStoreShim& other) const {
    return store_obj.equal(other.store_obj);
  }

  void DepositStratum(
    const HSTRAT_RANK_T rank,
    const hereditary_stratum_t& stratum
  ) {
    store_obj.attr("DepositStratum")(
      rank,
      stratum
    );
  }

  HSTRAT_RANK_T GetNumStrataRetained() const {
    return store_obj.attr(
      "GetNumStrataRetained"
    )().template cast<HSTRAT_RANK_T>();
  }

  template<typename F=hstrat_auxlib::Monostate>
  hereditary_stratum_t GetStratumAtColumnIndex(
    const HSTRAT_RANK_T index,
    F={}
  ) const {
    // ignore F for now, can use in future as optimization
    return store_obj.attr(
      "GetStratumAtColumnIndex"
    )(index).template cast<hereditary_stratum_t>();
  }

  HSTRAT_RANK_T GetRankAtColumnIndex(const HSTRAT_RANK_T index) const {
    // ignore F for now, can use in future as optimization
    return store_obj.attr(
      "GetRankAtColumnIndex"
    )(index).template cast<HSTRAT_RANK_T>();
  }

  HSTRAT_RANK_T GetColumnIndexOfRank(const HSTRAT_RANK_T index) const {
    // ignore F for now, can use in future as optimization
    return store_obj.attr(
      "GetColumnIndexOfRank"
    )(index).template cast<HSTRAT_RANK_T>();
  }


  template<typename F=hstrat_auxlib::Monostate>
  void DelRanks(
    cppcoro::generator<const HSTRAT_RANK_T> ranks,
    // deposition ranks might not be stored in strata
    F get_column_index_of_rank={}
  ) {
    if constexpr (std::is_same_v<F, hstrat_auxlib::Monostate>) {
      store_obj.attr("DelRanks")(ranks);
    } else {
      store_obj.attr("DelRanks")(
        ranks,
        std::function<HSTRAT_RANK_T(HSTRAT_RANK_T)>(get_column_index_of_rank)
      );
    }
  }

  cppcoro::generator<const HSTRAT_RANK_T> IterRetainedRanks() const {
    return store_obj.attr(
      "IterRetainedRanks"
    )().template cast<cppcoro::generator<const HSTRAT_RANK_T>>();
  }

  template<typename F=hstrat_auxlib::Monostate>
  cppcoro::generator<
    std::tuple<HSTRAT_RANK_T, typename hereditary_stratum_t::differentia_t>
  > IterRankDifferentia(
    const HSTRAT_RANK_T start_column_index = 0,
    F get_rank_at_column_index = {}
  ) const {
    using return_t = cppcoro::generator<
      std::tuple<
        HSTRAT_RANK_T,
        typename hereditary_stratum_t::differentia_t
      >
    >;
    if constexpr (std::is_same_v<F, hstrat_auxlib::Monostate>) {
      return store_obj.attr("DelRanks")(
        start_column_index
      ).template cast<return_t>();
    } else {
      return store_obj.attr("DelRanks")(
        start_column_index,
        std::function<HSTRAT_RANK_T(HSTRAT_RANK_T)>(get_rank_at_column_index)
      ).template cast<return_t>();
    }
  }

};

} // namespace hstrat_auxlib

#endif // #ifndef HSTRAT_PYBIND_PYOBJECTORDEREDSTORESHIM_HPP_INCLUDE
