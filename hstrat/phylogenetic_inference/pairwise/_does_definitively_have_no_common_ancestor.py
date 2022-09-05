from ...genome_instrumentation import HereditaryStratigraphicColumn
from ...juxtaposition import (
    calc_definitive_max_rank_of_first_retained_disparity_between,
)


def does_definitively_have_no_common_ancestor(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> bool:
    """Could self possibly share a common ancestor with other?

    Note that stratum rention policies are strictly required to permanently
    retain the most ancient stratum.

    See Also
    --------
    does_have_any_common_ancestor:
        Can we conclude with confidence_level confidence that self and other
        share a common ancestor?
    """
    first_disparity = self.CalcDefinitiveMaxRankOfFirstRetainedDisparityWith(
        other
    )
    return False if first_disparity is None else first_disparity == 0
