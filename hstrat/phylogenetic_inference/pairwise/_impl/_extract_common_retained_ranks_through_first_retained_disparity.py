import typing

from iterpop import iterpop as ip
import opytional as opyt

from ....genome_instrumentation import HereditaryStratigraphicColumn
from ....juxtaposition._impl import dispatch_impl


def extract_common_retained_ranks_through_first_retained_disparity(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.List[int]:

    # choose correct impl for columns/specimens
    impl = dispatch_impl(first, second)

    rank_of_first_retained_disparity_between = opyt.or_else(
        impl.calc_rank_of_first_retained_disparity_between(
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
        *impl.iter_ranks_of_retained_commonality_between(first, second),
        rank_of_first_retained_disparity_between,
    ]
