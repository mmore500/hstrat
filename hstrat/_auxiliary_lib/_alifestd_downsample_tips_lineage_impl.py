import numpy as np


def _select_target_id(
    is_leaf: np.ndarray,
    target_values: np.ndarray,
) -> int:
    """Select the target leaf id (largest target value, ties broken by RNG).

    Uses numpy's global RNG for tie-breaking.  Callers should wrap with
    ``with_rng_state_context`` when deterministic behaviour is required.

    Parameters
    ----------
    is_leaf : numpy.ndarray
        Boolean array indicating which taxa are leaves.
    target_values : numpy.ndarray
        Values used to select the target leaf (all taxa).

    Returns
    -------
    int
        The id of the selected target leaf.
    """
    ids = np.arange(len(is_leaf))
    leaf_ids = ids[is_leaf]
    leaf_target_values = target_values[is_leaf]
    max_target = leaf_target_values.max()
    candidate_ids = leaf_ids[leaf_target_values == max_target]
    return int(np.random.choice(candidate_ids))


def _alifestd_downsample_tips_lineage_impl(
    is_leaf: np.ndarray,
    criterion_values: np.ndarray,
    num_tips: int,
    mrca_vector: np.ndarray,
) -> np.ndarray:
    """Shared numpy implementation for lineage-based tip downsampling.

    Computes off-lineage deltas from a pre-computed MRCA vector and
    returns a boolean extant mask.

    Parameters
    ----------
    is_leaf : numpy.ndarray
        Boolean array indicating which taxa are leaves.
    criterion_values : numpy.ndarray
        Values used to compute off-lineage delta (all taxa).
    num_tips : int
        Number of tips to retain.
    mrca_vector : numpy.ndarray
        Integer array of MRCA ids for each taxon with respect to the
        target leaf.  Taxa in a different tree should have ``-1``.

    Returns
    -------
    numpy.ndarray
        Boolean array of length ``len(is_leaf)`` marking retained taxa.
    """
    ids = np.arange(len(is_leaf))

    # Taxa with no common ancestor (different tree) get -1 from MRCA
    # calc; replace with the taxon's own id so the lookup doesn't fail,
    # then exclude these taxa from selection below.
    no_mrca_mask = mrca_vector == -1
    safe_mrca = np.where(no_mrca_mask, ids, mrca_vector)

    # Off-lineage delta
    off_lineage_delta = np.abs(
        criterion_values - criterion_values[safe_mrca],
    )

    # Select eligible leaves with the smallest deltas
    is_eligible = is_leaf & ~no_mrca_mask
    eligible_ids = ids[is_eligible]
    eligible_deltas = off_lineage_delta[is_eligible]
    order = np.argsort(eligible_deltas, kind="stable")
    kept_ids = eligible_ids[order[:num_tips]]

    # Build extant mask
    return np.bincount(kept_ids, minlength=len(ids)).astype(bool)
