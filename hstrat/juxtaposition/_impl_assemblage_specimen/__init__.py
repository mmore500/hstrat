"""Implementation helpers."""

from ._calc_rank_of_first_retained_disparity_between_bsearch import (
    calc_rank_of_first_retained_disparity_between_bsearch,
)
from ._calc_rank_of_first_retained_disparity_between_naive import (
    calc_rank_of_first_retained_disparity_between_naive,
)

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "calc_rank_of_first_retained_disparity_between_bsearch",
    "calc_rank_of_first_retained_disparity_between_naive",
]
