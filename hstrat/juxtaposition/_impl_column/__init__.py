"""Implementation helpers."""

from ._calc_rank_of_first_retained_disparity_between import (
    calc_rank_of_first_retained_disparity_between,
)
from ._calc_rank_of_first_retained_disparity_between_bsearch import (
    calc_rank_of_first_retained_disparity_between_bsearch,
)
from ._calc_rank_of_first_retained_disparity_between_generic import (
    calc_rank_of_first_retained_disparity_between_generic,
)
from ._calc_rank_of_last_retained_commonality_between import (
    calc_rank_of_last_retained_commonality_between,
)
from ._calc_rank_of_last_retained_commonality_between_bsearch import (
    calc_rank_of_last_retained_commonality_between_bsearch,
)
from ._calc_rank_of_last_retained_commonality_between_generic import (
    calc_rank_of_last_retained_commonality_between_generic,
)
from ._calc_rank_of_parity_segue_between import (
    calc_rank_of_parity_segue_between,
)
from ._iter_mutual_ranks import iter_mutual_ranks
from ._iter_ranks_of_retained_commonality_between import (
    iter_ranks_of_retained_commonality_between,
)

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "calc_rank_of_first_retained_disparity_between",
    "calc_rank_of_first_retained_disparity_between_bsearch",
    "calc_rank_of_first_retained_disparity_between_generic",
    "calc_rank_of_last_retained_commonality_between",
    "calc_rank_of_last_retained_commonality_between_bsearch",
    "calc_rank_of_last_retained_commonality_between_generic",
    "calc_rank_of_parity_segue_between",
    "iter_mutual_ranks",
    "iter_ranks_of_retained_commonality_between",
]
