"""Functions that compare two columns.

Provides the foundation for phylogenetic inference tools.
"""

from ._calc_definitive_max_rank_of_first_retained_disparity_between import (
    calc_definitive_max_rank_of_first_retained_disparity_between,
)
from ._calc_definitive_max_rank_of_last_retained_commonality_between import (
    calc_definitive_max_rank_of_last_retained_commonality_between,
)
from ._calc_definitive_min_ranks_since_first_retained_disparity_with import (
    calc_definitive_min_ranks_since_first_retained_disparity_with,
)
from ._calc_definitive_min_ranks_since_last_retained_commonality_with import (
    calc_definitive_min_ranks_since_last_retained_commonality_with,
)
from ._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from ._calc_probability_differentia_collision_between import (
    calc_probability_differentia_collision_between,
)
from ._calc_rank_of_first_retained_disparity_between import (
    calc_rank_of_first_retained_disparity_between,
)
from ._calc_rank_of_last_retained_commonality_between import (
    calc_rank_of_last_retained_commonality_between,
)
from ._calc_ranks_since_first_retained_disparity_with import (
    calc_ranks_since_first_retained_disparity_with,
)
from ._calc_ranks_since_last_retained_commonality_with import (
    calc_ranks_since_last_retained_commonality_with,
)
from ._diff_retained_ranks import diff_retained_ranks
from ._get_last_common_stratum_between import get_last_common_stratum_between
from ._get_nth_common_rank_between import get_nth_common_rank_between

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "calc_definitive_max_rank_of_first_retained_disparity_between",
    "calc_definitive_max_rank_of_last_retained_commonality_between",
    "calc_definitive_min_ranks_since_first_retained_disparity_with",
    "calc_definitive_min_ranks_since_last_retained_commonality_with",
    "calc_min_implausible_spurious_consecutive_differentia_collisions_between",
    "calc_probability_differentia_collision_between",
    "calc_rank_of_first_retained_disparity_between",
    "calc_rank_of_last_retained_commonality_between",
    "calc_ranks_since_first_retained_disparity_with",
    "calc_ranks_since_last_retained_commonality_with",
    "diff_retained_ranks",
    "get_last_common_stratum_between",
    "get_nth_common_rank_between",
]

from .._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
