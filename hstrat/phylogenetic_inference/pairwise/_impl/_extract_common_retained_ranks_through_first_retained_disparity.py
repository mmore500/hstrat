import typing

from iterpop import iterpop as ip
import opytional as opyt

from ....genome_instrumentation import HereditaryStratigraphicColumn
from ....juxtaposition import calc_rank_of_first_retained_disparity_between
from ....juxtaposition._impl import (
    iter_ranks_of_retained_commonality_between_generic,
)


def extract_common_retained_ranks_through_first_retained_disparity(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.List[int]:

    ranks_of_retained_commonality_between = [
        *iter_ranks_of_retained_commonality_between_generic(first, second)
    ]

    rank_of_first_retained_disparity_between = opyt.or_else(
        calc_rank_of_first_retained_disparity_between(
            first,
            second,
            confidence_level=0.49,
        ),
        lambda: ip.pophomogeneous(
            (
                first.GetNumStrataDeposited(),
                second.GetNumStrataDeposited(),
            )
        ),
    )
    return [
        *ranks_of_retained_commonality_between,
        rank_of_first_retained_disparity_between,
    ]
