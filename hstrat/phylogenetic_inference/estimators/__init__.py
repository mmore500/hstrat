"""Tools to estimate MRCA generation from shared ranks of commonality and
disparity."""

from ._estimate_rank_of_mrca_maximum_likelihood import (
    estimate_rank_of_mrca_maximum_likelihood,
)
from ._estimate_rank_of_mrca_naive import estimate_rank_of_mrca_naive
from ._estimate_rank_of_mrca_unbiased import estimate_rank_of_mrca_unbiased

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "estimate_rank_of_mrca_maximum_likelihood",
    "estimate_rank_of_mrca_naive",
    "estimate_rank_of_mrca_unbiased",
]
