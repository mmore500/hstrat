#pragma once
#ifndef HSTRAT_PYBIND_CUSTOM_CASTERS_HPP_INCLUDE
#define HSTRAT_PYBIND_CUSTOM_CASTERS_HPP_INCLUDE

#include <iostream>
#include <tuple>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include "../../third-party/cppcoro/include/cppcoro/generator.hpp"

#include "../hstrat/config/HSTRAT_RANK_T.hpp"


// https://github.com/pybind/pybind11/issues/1176#issuecomment-343312352
namespace pybind11 { namespace detail {

using quadword_tuple_t = std::tuple<HSTRAT_RANK_T, uint64_t>;
using quadword_tuple_generator_t = cppcoro::generator<quadword_tuple_t>;
using cast_t = quadword_tuple_generator_t;

template <> struct type_caster<cast_t> : public type_caster_base<cast_t> {
    using base = type_caster_base<cast_t>;
public:
    bool load(handle src, bool convert) {
        if (base::load(src, convert)) {
            // std::cerr << "loaded via base!\n";
            return true;
        }
        std::cerr << "failed via base!\n";
        // else if (py::isinstance<py::int_>(src)) {
        //     std::cerr << "loading from integer!\n";
        //     value = new cast_t(py::cast<int>(src));
        //     return true;
        // }

        return false;
    }

    static handle cast(cast_t *src, return_value_policy policy, handle parent) {
        /* Do any additional work here */
        std::cerr << "cast via base!\n";
        return base::cast(src, policy, parent);
    }

    static handle cast(const cast_t& src, return_value_policy policy, handle parent) {
        /* Do any additional work here */
        std::cerr << "cast via base2!\n";
        return base::cast(src, policy, parent);
    }

    static handle cast(cast_t&& src, return_value_policy policy, handle parent) {
        /* Do any additional work here */
        std::cerr << "cast via base3!\n";
        return base::cast(std::move(src), policy, parent);
    }
};

}}

#endif // #ifndef HSTRAT_PYBIND_CUSTOM_CASTERS_HPP_INCLUDE
