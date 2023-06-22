#include <numeric>
#include <vector>

#include "Catch2/single_include/catch2/catch.hpp"

#include "hstrat_auxlib/binary_search.hpp"


TEST_CASE("Test binary_search") {
  for (std::size_t len{}; len < 10; ++len) {
    for (std::size_t target{}; target < len; ++target) {
      std::vector<std::size_t> v(len);
      std::iota(std::begin(v), std::end(v), std::size_t{});

      REQUIRE(
        hstrat_auxlib::binary_search(
          [target, &v](std::size_t x){ return v[x] >= target; },
          v.size()
        )
        == target
      );
    }
  }
}
