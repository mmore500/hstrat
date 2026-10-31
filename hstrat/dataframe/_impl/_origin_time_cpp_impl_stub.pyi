import typing

import numpy as np

def brute_upgma(
    tip_T: np.ndarray,
    tip_off: np.ndarray,
    tip_ranks: np.ndarray,
    tip_diffs: np.ndarray,
    p: float,
    t0: float,
) -> typing.Tuple[np.ndarray, np.ndarray]: ...
def cross_pair_sums(
    ancestor_ids: np.ndarray,
    ranks: np.ndarray,
    tip_of_node: np.ndarray,
    tip_T: np.ndarray,
    tip_off: np.ndarray,
    tip_ranks: np.ndarray,
    tip_diffs: np.ndarray,
    p: float,
    t0: float,
) -> typing.Tuple[np.ndarray, np.ndarray]: ...
def pair_estimate(
    tip_T: np.ndarray,
    tip_off: np.ndarray,
    tip_ranks: np.ndarray,
    tip_diffs: np.ndarray,
    p: float,
    t0: float,
    a: int,
    b: int,
) -> float: ...
def pool_inversions(
    ancestor_ids: np.ndarray,
    times: np.ndarray,
    weights: np.ndarray,
) -> typing.Tuple[np.ndarray, int]: ...
def scaffold_upgma(
    tip_T: np.ndarray,
    tip_off: np.ndarray,
    tip_ranks: np.ndarray,
    tip_diffs: np.ndarray,
    p: float,
    t0: float,
    trie_ancestor_ids: np.ndarray,
    trie_tip_of_node: np.ndarray,
    k: int = 5,
    pool_size: int = 10,
    n_samples: int = 64,
    direct_max: int = 64,
    seed: int = 1,
) -> typing.Tuple[np.ndarray, np.ndarray, typing.Dict[str, int]]: ...
