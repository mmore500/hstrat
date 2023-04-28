import pytest

from hstrat import hstrat
from hstrat.genome_instrumentation import stratum_ordered_stores


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_deposition(impl):
    store1 = impl()
    assert store1.GetNumStrataRetained() == 0

    stratum1 = hstrat.HereditaryStratum(deposition_rank=0)
    store1.DepositStratum(0, stratum1)
    assert store1.GetNumStrataRetained() == 1
    assert store1.GetStratumAtColumnIndex(0) == stratum1

    store2 = store1.Clone()

    stratum2 = hstrat.HereditaryStratum(deposition_rank=1)
    store1.DepositStratum(1, stratum2)
    assert store1.GetNumStrataRetained() == 2
    assert store1.GetStratumAtColumnIndex(1) == stratum2
    assert store1.GetStratumAtColumnIndex(0) != stratum2

    assert store2.GetNumStrataRetained() == 1
    assert store2.GetStratumAtColumnIndex(0) == stratum1


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_deletion1(impl):
    store1 = impl()
    stratum1 = hstrat.HereditaryStratum(deposition_rank=0)
    store1.DepositStratum(0, stratum1)

    store2 = store1.Clone()
    stratum2 = hstrat.HereditaryStratum(deposition_rank=1)
    store1.DepositStratum(1, stratum2)

    del store1
    assert store2.GetNumStrataRetained() == 1
    assert store2.GetStratumAtColumnIndex(0) == stratum1


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_deletion2(impl):
    store1 = impl()
    stratum1 = hstrat.HereditaryStratum(deposition_rank=0)
    store1.DepositStratum(0, stratum1)

    store2 = store1.Clone()
    stratum2 = hstrat.HereditaryStratum(deposition_rank=1)
    store1.DepositStratum(1, stratum2)

    del store2
    assert store1.GetNumStrataRetained() == 2
    assert store1.GetStratumAtColumnIndex(0) == stratum1
    assert store1.GetStratumAtColumnIndex(1) == stratum2


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_equality(impl):
    assert impl() == impl()

    store1 = impl()
    store1.DepositStratum(0, hstrat.HereditaryStratum(deposition_rank=0))
    store2 = store1.Clone()
    assert store1 == store2

    store2.DepositStratum(1, hstrat.HereditaryStratum(deposition_rank=1))
    assert store1 != store2


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_GetRankAtColumnIndex(impl):
    store1 = impl()
    store1.DepositStratum(0, hstrat.HereditaryStratum(deposition_rank=0))
    store1.DepositStratum(1, hstrat.HereditaryStratum(deposition_rank=1))
    store1.DepositStratum(2, hstrat.HereditaryStratum(deposition_rank=2))
    assert store1.GetRankAtColumnIndex(0) == 0
    assert store1.GetRankAtColumnIndex(1) == 1
    assert store1.GetRankAtColumnIndex(2) == 2

    store1.DelRanks([1])
    assert store1.GetRankAtColumnIndex(0) == 0
    assert store1.GetRankAtColumnIndex(1) == 2


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_GetStratumAtColumnIndex(impl):
    store1 = impl()
    strata = [
        hstrat.HereditaryStratum(deposition_rank=rank) for rank in range(3)
    ]
    for rank, stratum in enumerate(strata):
        store1.DepositStratum(rank, stratum)

    for rank, stratum in enumerate(strata):
        assert store1.GetStratumAtColumnIndex(rank) == strata[rank]

    store1.DelRanks([1])
    assert store1.GetStratumAtColumnIndex(0) == strata[0]
    assert store1.GetStratumAtColumnIndex(1) == strata[2]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_GetNumStrataRetained(impl):
    store1 = impl()
    for rank in range(5):
        assert store1.GetNumStrataRetained() == rank
        store1.DepositStratum(rank, hstrat.HereditaryStratum())
    assert store1.GetNumStrataRetained() == 5

    store1.DelRanks([1, 2], get_column_index_of_rank=lambda x: x)
    assert store1.GetNumStrataRetained() == 3

    store1.DepositStratum(5, hstrat.HereditaryStratum())
    assert store1.GetNumStrataRetained() == 4

    store1.DelRanks(
        [5],
        get_column_index_of_rank=lambda x: {
            3: 0,
            5: 1,
        }[x],
    )
    assert store1.GetNumStrataRetained() == 3


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_GetColumnIndexOfRank(impl):
    store1 = impl()
    ranks = [0, 8, 42, 63]
    for rank in ranks:
        store1.DepositStratum(
            rank=rank,
            stratum=hstrat.HereditaryStratum(deposition_rank=rank),
        )

    assert store1.GetColumnIndexOfRank(0) == 0
    assert store1.GetColumnIndexOfRank(1) is None
    assert store1.GetColumnIndexOfRank(4) is None
    assert store1.GetColumnIndexOfRank(7) is None
    assert store1.GetColumnIndexOfRank(8) == 1
    assert store1.GetColumnIndexOfRank(42) == 2
    assert store1.GetColumnIndexOfRank(63) == 3
    assert store1.GetColumnIndexOfRank(64) is None
    assert store1.GetColumnIndexOfRank(100) is None


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_IterRetainedRanks(impl):
    store1 = impl()
    ranks = [0, 8, 42, 63]
    for i, rank in enumerate(ranks):
        assert store1.GetNumStrataRetained() == i
        assert len([*store1.IterRetainedRanks()]) == i
        store1.DepositStratum(
            rank=rank,
            stratum=hstrat.HereditaryStratum(deposition_rank=rank),
        )

    res = [*store1.IterRetainedRanks()]
    assert len(res) == len(set(res))
    assert set(res) == set(ranks)


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_IterRetainedStrata(impl):
    store1 = impl()
    strata = [
        hstrat.HereditaryStratum(deposition_rank=rank) for rank in range(5)
    ]
    assert len(strata) == len(set(map(id, strata)))
    for rank, stratum in enumerate(strata):
        assert store1.GetNumStrataRetained() == rank
        assert len([*store1.IterRetainedStrata()]) == rank
        store1.DepositStratum(stratum=stratum, rank=rank)

    res = [*store1.IterRetainedStrata()]
    assert len(res) == 5
    assert len(res) == len(set(map(id, res)))
    assert sorted(res) == sorted(strata)


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_IterRankDifferentia1(impl):
    store1 = impl()
    ranks = [0, 8, 42, 63]
    strata = [hstrat.HereditaryStratum(deposition_rank=rank) for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    assert [*zip(ranks, [stratum.GetDifferentia() for stratum in strata])] == [
        *store1.IterRankDifferentiaZip()
    ]
    assert [*zip(ranks, [stratum.GetDifferentia() for stratum in strata])][
        0:
    ] == [*store1.IterRankDifferentiaZip(start_column_index=0)]
    assert [*zip(ranks, [stratum.GetDifferentia() for stratum in strata])][
        2:
    ] == [*store1.IterRankDifferentiaZip(start_column_index=2)]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_IterRankDifferentia2(impl):
    store1 = impl()
    ranks = [0, 8, 42, 63]
    strata = [hstrat.HereditaryStratum(deposition_rank=rank) for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    def col_index_to_rank(column_idx):
        return ranks[column_idx]

    assert [*zip(ranks, [stratum.GetDifferentia() for stratum in strata])] == [
        *store1.IterRankDifferentiaZip(
            get_rank_at_column_index=col_index_to_rank,
        )
    ]
    assert [*zip(ranks, [stratum.GetDifferentia() for stratum in strata])][
        0:
    ] == [
        *store1.IterRankDifferentiaZip(
            get_rank_at_column_index=col_index_to_rank,
            start_column_index=0,
        )
    ]
    assert [*zip(ranks, [stratum.GetDifferentia() for stratum in strata])][
        2:
    ] == [
        *store1.IterRankDifferentiaZip(
            get_rank_at_column_index=col_index_to_rank,
            start_column_index=2,
        )
    ]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_getrank_impl1(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63]
    strata = [hstrat.HereditaryStratum(deposition_rank=rank) for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [8, 42],
        [],
        [55],
        [],
        [0, 63],
        [],
    ):
        store1.DelRanks(deletion)
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [*store1.IterRankDifferentiaZip()]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_getrank_impl2(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63]
    strata = [hstrat.HereditaryStratum(deposition_rank=rank) for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [0, 63],
        [],
        [8],
        [],
        [55],
        [],
        [42],
        [],
    ):
        store1.DelRanks(deletion)
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [*store1.IterRankDifferentiaZip()]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_getrank_impl3(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63, 80]
    strata = [hstrat.HereditaryStratum(deposition_rank=rank) for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [0, 80],
        [],
        [63],
        [],
        [8, 55],
        [],
        [42],
        [],
    ):
        store1.DelRanks(deletion)
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [*store1.IterRankDifferentiaZip()]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_getrank_impl4(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63]
    strata = [hstrat.HereditaryStratum(deposition_rank=rank) for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [55, 63],
        [],
        [0, 8],
        [],
        [42],
        [],
    ):
        store1.DelRanks(deletion)
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [*store1.IterRankDifferentiaZip()]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_getrank_impl5(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63]
    strata = [hstrat.HereditaryStratum(deposition_rank=rank) for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [42, 63],
        [],
        [0, 8, 55],
        [],
    ):
        store1.DelRanks(deletion)
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [*store1.IterRankDifferentiaZip()]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_calcrank_impl1(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63]
    strata = [hstrat.HereditaryStratum() for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [8, 42],
        [],
        [55],
        [],
        [0, 63],
        [],
    ):
        store1.DelRanks(
            get_column_index_of_rank=lambda rank: ranks.index(rank),
            ranks=deletion,
        )
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [
            *store1.IterRankDifferentiaZip(
                get_rank_at_column_index=lambda idx: ranks[idx],
            )
        ]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_calcrank_impl2(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63]
    strata = [hstrat.HereditaryStratum() for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [0, 63],
        [],
        [8],
        [],
        [55],
        [],
        [42],
        [],
    ):
        store1.DelRanks(
            get_column_index_of_rank=lambda rank: ranks.index(rank),
            ranks=deletion,
        )
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [
            *store1.IterRankDifferentiaZip(
                get_rank_at_column_index=lambda idx: ranks[idx],
            )
        ]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_calcrank_impl3(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63, 80]
    strata = [hstrat.HereditaryStratum() for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [0, 80],
        [],
        [63],
        [],
        [8, 55],
        [],
        [42],
        [],
    ):
        store1.DelRanks(
            get_column_index_of_rank=lambda rank: ranks.index(rank),
            ranks=deletion,
        )
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [
            *store1.IterRankDifferentiaZip(
                get_rank_at_column_index=lambda idx: ranks[idx],
            )
        ]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_calcrank_impl4(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63]
    strata = [hstrat.HereditaryStratum() for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [55, 63],
        [],
        [0, 8],
        [],
        [42],
        [],
    ):
        store1.DelRanks(
            get_column_index_of_rank=lambda rank: ranks.index(rank),
            ranks=deletion,
        )
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [
            *store1.IterRankDifferentiaZip(
                get_rank_at_column_index=lambda idx: ranks[idx],
            )
        ]


@pytest.mark.parametrize(
    "impl",
    stratum_ordered_stores._HereditaryStratumOrderedStoreList_.impls,
)
def test_DelRanks_calcrank_impl5(impl):
    store1 = impl()
    ranks = [0, 8, 42, 55, 63]
    strata = [hstrat.HereditaryStratum() for rank in ranks]
    for rank, stratum in zip(ranks, strata):
        store1.DepositStratum(rank=rank, stratum=stratum)

    for deletion in (
        [],
        [42, 63],
        [],
        [0, 8, 55],
        [],
    ):
        store1.DelRanks(
            get_column_index_of_rank=lambda rank: ranks.index(rank),
            ranks=deletion,
        )
        for rank in deletion:
            del strata[ranks.index(rank)]
            ranks.remove(rank)
        assert [
            *zip(ranks, [stratum.GetDifferentia() for stratum in strata])
        ] == [
            *store1.IterRankDifferentiaZip(
                get_rank_at_column_index=lambda idx: ranks[idx],
            )
        ]
