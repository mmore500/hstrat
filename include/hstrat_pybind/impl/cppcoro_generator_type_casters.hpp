#pragma once
#ifndef HSTRAT_PYBIND_IMPL_CPPCORO_GENERATOR_TYPE_CASTERS_HPP_INCLUDE
#define HSTRAT_PYBIND_IMPL_CPPCORO_GENERATOR_TYPE_CASTERS_HPP_INCLUDE

#include <cassert>
#include <tuple>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include "../../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../../hstrat/config/HSTRAT_RANK_T.hpp"
#include "../../hstrat/genome_instrumentation/HereditaryStratum.hpp"

#include "../pyobject.hpp"

#define HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(generator_t) template <>\
struct type_caster<generator_t> : public type_caster_base<generator_t> {\
\
    using base_t = type_caster_base<generator_t>;\
\
    bool load(handle src, bool convert) { return base_t::load(src, convert); }\
\
    static handle cast(\
      generator_t *src, return_value_policy policy, handle parent\
    ) { assert(false); return base_t::cast(src, policy, parent); }\
\
    static handle cast(\
      const generator_t& src, return_value_policy policy, handle parent\
    ) { assert(false); return base_t::cast(src, policy, parent); }\
\
    static handle cast(\
      generator_t&& src, return_value_policy policy, handle parent\
    ) {\
        auto handle = base_t::cast(std::move(src), policy, parent);\
        auto iter_ = py::module::import("builtins").attr("iter");\
        auto res = iter_(handle);\
        return res.release();\
    }\
\
}

namespace hstrat_pybind::detail {
  using rank_generator_t = cppcoro::generator<const HSTRAT_RANK_T>;

  using bit_tuple_t = std::tuple<HSTRAT_RANK_T, bool>;
  using bit_tuple_generator_t = cppcoro::generator<bit_tuple_t>;

  using byte_tuple_t = std::tuple<HSTRAT_RANK_T, uint8_t>;
  using byte_tuple_generator_t = cppcoro::generator<byte_tuple_t>;

  using word_tuple_t = std::tuple<HSTRAT_RANK_T, uint16_t>;
  using word_tuple_generator_t = cppcoro::generator<word_tuple_t>;

  using doubleword_tuple_t = std::tuple<HSTRAT_RANK_T, uint32_t>;
  using doubleword_tuple_generator_t = cppcoro::generator<doubleword_tuple_t>;

  using quadword_tuple_t = std::tuple<HSTRAT_RANK_T, uint64_t>;
  using quadword_tuple_generator_t = cppcoro::generator<quadword_tuple_t>;

  using bit_deporank_t = hstrat::HereditaryStratum<
    bool, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using bit_deporank_generator_t = cppcoro::generator<bit_deporank_t>;

  using byte_deporank_t = hstrat::HereditaryStratum<
    uint8_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using byte_deporank_generator_t = cppcoro::generator<byte_deporank_t>;

  using word_deporank_t = hstrat::HereditaryStratum<
    uint16_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using word_deporank_generator_t = cppcoro::generator<word_deporank_t>;

  using doubleword_deporank_t = hstrat::HereditaryStratum<
    uint32_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using doubleword_deporank_generator_t = cppcoro::generator<
    doubleword_deporank_t>;

  using quadword_deporank_t = hstrat::HereditaryStratum<
    uint64_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject, // ANNOTATION_T
    HSTRAT_RANK_T // DEPOSITION_RANK_T
  >;
  using quadword_deporank_generator_t = cppcoro::generator<
    quadword_deporank_t>;

  using bit_nodeporank_t = hstrat::HereditaryStratum<
    bool, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using bit_nodeporank_generator_t = cppcoro::generator<bit_nodeporank_t>;

  using byte_nodeporank_t = hstrat::HereditaryStratum<
    uint8_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using byte_nodeporank_generator_t = cppcoro::generator<
    byte_nodeporank_t>;

  using word_nodeporank_t = hstrat::HereditaryStratum<
    uint16_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using word_nodeporank_generator_t = cppcoro::generator<
    word_nodeporank_t>;

  using doubleword_nodeporank_t = hstrat::HereditaryStratum<
    uint32_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using doubleword_nodeporank_generator_t = cppcoro::generator<
    doubleword_nodeporank_t>;

  using quadword_nodeporank_t = hstrat::HereditaryStratum<
    uint64_t, // DIFFERENTIA_T
    hstrat_pybind::pyobject // ANNOTATION_T
  >;
  using quadword_nodeporank_generator_t = cppcoro::generator<
    quadword_nodeporank_t>;

}

// https://github.com/pybind/pybind11/issues/1176#issuecomment-343312352
namespace pybind11::detail {

HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::rank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::bit_tuple_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::byte_tuple_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::word_tuple_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::doubleword_tuple_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::quadword_tuple_generator_t
);

HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::bit_deporank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::byte_deporank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::word_deporank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::doubleword_deporank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::quadword_deporank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::bit_nodeporank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::byte_nodeporank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::word_nodeporank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::doubleword_nodeporank_generator_t
);
HSTRAT_PYBIND_GENERATOR_TYPE_CASTER(
  hstrat_pybind::detail::quadword_nodeporank_generator_t
);

} // namespace pybind11::detail

#endif // #ifndef HSTRAT_PYBIND_IMPL_CPPCORO_GENERATOR_TYPE_CASTERS_HPP_INCLUDE
