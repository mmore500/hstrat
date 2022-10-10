#pragma once
#ifndef HSTRAT_CONFIG_HSTRAT_RANK_T_HPP_INCLUDE
#define HSTRAT_CONFIG_HSTRAT_RANK_T_HPP_INCLUDE

#include <concepts>
#include <cstdint>

#ifndef HSTRAT_RANK_T
#define HSTRAT_RANK_T int64_t
#endif // #ifndef HSTRAT_RANK_T

namespace hstrat {

template<class T> concept RankTConcept = std::same_as<T, HSTRAT_RANK_T>;

} // namespae hstrat

#endif // #ifndef HSTRAT_CONFIG_HSTRAT_RANK_T_HPP_INCLUDE
