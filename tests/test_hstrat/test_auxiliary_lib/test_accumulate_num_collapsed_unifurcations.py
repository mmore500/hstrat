import numpy as np
import pandas as pd
from phyloframe import legacy as pfl

from hstrat._auxiliary_lib import accumulate_num_collapsed_unifurcations


def test_empty():
    res = accumulate_num_collapsed_unifurcations(np.array([], dtype=int))
    assert len(res) == 0


def test_no_unifurcations():
    # 0 <- 1, 2
    res = accumulate_num_collapsed_unifurcations(np.array([0, 0, 0]))
    np.testing.assert_array_equal(res, [0, 0, 0])


def test_branched_tree():
    # 0 <- 1 <- 2 <- 3 <- 5 <- 6
    #            \ <- 4
    ancestor_ids = np.array([0, 0, 1, 2, 2, 3, 5])
    res = accumulate_num_collapsed_unifurcations(ancestor_ids)
    keep = [0, 2, 4, 6]
    np.testing.assert_array_equal(res[keep], [0, 1, 0, 2])


def test_prior_counts():
    ancestor_ids = np.array([0, 0, 1, 2, 2, 3, 5])
    prior = np.array([0, 4, 1, 0, 2, 0, 3])
    res = accumulate_num_collapsed_unifurcations(ancestor_ids, prior)
    keep = [0, 2, 4, 6]
    # node 2: 1 + (4 + 1); node 4: 2; node 6: 3 + (0 + 1) + (3 + 1) - 3...
    # ... i.e., own 0 + collapsed node 5 (3 + 1) + collapsed node 3 (0 + 1)
    np.testing.assert_array_equal(res[keep], [0, 6, 2, 5])


def test_unifurcating_root_kept():
    # 0 <- 1 <- 2
    ancestor_ids = np.array([0, 0, 1])
    res = accumulate_num_collapsed_unifurcations(ancestor_ids)
    assert res[0] == 0
    assert res[2] == 1


def test_consistent_with_alifestd_collapse_unifurcations():
    np.random.seed(1)
    for __ in range(20):
        n = 50
        ancestor_ids = np.array(
            [0] + [np.random.randint(max(i - 3, 0), i) for i in range(1, n)],
        )
        df = pd.DataFrame(
            {
                "id": np.arange(n),
                "ancestor_id": ancestor_ids,
                "num_collapsed": accumulate_num_collapsed_unifurcations(
                    ancestor_ids
                ),
            },
        )
        collapsed = pfl.alifestd_collapse_unifurcations(df)
        # number of collapsed nodes is total minus kept
        assert collapsed["num_collapsed"].sum() == n - len(collapsed)
