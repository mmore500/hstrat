import numpy as np
import polars as pl

from ._alifestd_from_newick import _extract_labels
from ._alifestd_from_newick import _parse_newick


def alifestd_from_newick_polars(
    newick: str,
) -> pl.DataFrame:
    """Convert a Newick format string to a phylogeny dataframe.

    Parses a Newick tree string and returns a polars DataFrame in alife
    standard format with columns: id, ancestor_list, ancestor_id,
    taxon_label, origin_time_delta, and branch_length.

    Parameters
    ----------
    newick : str
        A phylogeny in Newick format.

    Returns
    -------
    pl.DataFrame
        Phylogeny dataframe in alife standard format.

    See Also
    --------
    alifestd_from_newick :
        Pandas-based implementation.
    alifestd_as_newick_asexual :
        Inverse conversion, from alife standard to Newick format.
    """
    newick = newick.strip()
    if not newick:
        return pl.DataFrame(
            {
                "id": pl.Series([], dtype=pl.Int64),
                "ancestor_list": pl.Series([], dtype=pl.Utf8),
                "ancestor_id": pl.Series([], dtype=pl.Int64),
                "taxon_label": pl.Series([], dtype=pl.Utf8),
                "origin_time_delta": pl.Series([], dtype=pl.Float64),
                "branch_length": pl.Series([], dtype=pl.Float64),
            }
        )

    chars = np.frombuffer(newick.encode("ascii"), dtype=np.uint8)
    n = len(chars)

    ids, ancestor_ids, branch_lengths, has_branch_length, label_start_stops = (
        _parse_newick(chars, n)
    )

    labels = _extract_labels(newick, chars, label_start_stops)

    origin_time_deltas = branch_lengths.copy()

    # build ancestor_list column
    ancestor_list = []
    for id_, anc_id in zip(ids, ancestor_ids):
        if id_ == anc_id:
            ancestor_list.append("[none]")
        else:
            ancestor_list.append(f"[{anc_id}]")

    return pl.DataFrame(
        {
            "id": pl.Series(ids, dtype=pl.Int64),
            "ancestor_list": pl.Series(ancestor_list, dtype=pl.Utf8),
            "ancestor_id": pl.Series(ancestor_ids, dtype=pl.Int64),
            "taxon_label": pl.Series(labels.tolist(), dtype=pl.Utf8),
            "origin_time_delta": pl.Series(origin_time_deltas, dtype=pl.Float64),
            "branch_length": pl.Series(branch_lengths, dtype=pl.Float64),
        }
    )
