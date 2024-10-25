from copy import copy
import itertools as it
import typing

import anytree

from ..._auxiliary_lib import AnyTreeAscendingIter
from .._HereditaryStratum import HereditaryStratum
from ._detail import HereditaryStratumOrderedStoreBase


class HereditaryStratumOrderedStoreTree(HereditaryStratumOrderedStoreBase):
    """Interchangeable backing container for HereditaryStratigraphicColumn.

    Stores deposited strata as a linked tree. Retained strata pertinent to the
    store are essentially a linear linked list reaching from tree leaf (most
    recent stratum) back to the tree root (most ancient stratum). Cloned stores
    directly share common components of the tree and then branch out different
    leaves as subsequent strata are deposited. Stratum deletion results in the
    entire strata sequence more recent than the deleted stratum being copied
    into an independent branch for the store that requested the deletion.

    Potentially useful in scenarios where stratum deletions are uncommon (i.e.,
    the perfect resolution stratum retention policy) or column cloning occurs heavily without much stratum deposition.
    """

    __slots__ = (
        "_leaf",
        "_num_strata_retained",
    )

    # strata stored in a tree with most ancient as root and most recent as leaf
    _leaf: anytree.AnyNode  # will contain HereditaryStratum
    # maintaining a counter is much more efficient than counting steps from leaf
    # to root
    _num_strata_retained: int

    def __init__(self: "HereditaryStratumOrderedStoreTree"):
        """Initialize instance variables."""
        self._leaf = None
        self._num_strata_retained = 0

    def __del__(self: "HereditaryStratumOrderedStoreTree"):
        """Destruct the store.

        Releases resources no longer needed by this store that are needed by no
        other stores.

        anytree uses bidirectional references between nodes so manual pruning
        is necessary because garbage collection won't recognize unused nodes as
        fully unreachable.
        """
        # delete all nodes that only lead to this store's leaf
        for node in self._GetAscendingIter():
            if sum(1 for _ in zip(node.children, range(2))) == 2:
                # if node has more than one child, stop deleting
                break
            else:
                # delete and keep ascending
                node.parent = None
                del node

    def __eq__(
        self: "HereditaryStratumOrderedStoreTree",
        other: "HereditaryStratumOrderedStoreTree",
    ) -> bool:
        """Compare for value-wise equality."""
        return isinstance(other, self.__class__) and (
            self._leaf.stratum if self._leaf is not None else None,
            self._num_strata_retained,
        ) == (
            other._leaf.stratum if other._leaf is not None else None,
            other._num_strata_retained,
        )

    def _GetAscendingIter(
        self: "HereditaryStratumOrderedStoreTree",
    ) -> typing.Iterator[anytree.AnyNode]:
        """Iterate over retained strata from most recent to most ancient."""
        return AnyTreeAscendingIter(self._leaf)

    def DepositStratum(
        self: "HereditaryStratumOrderedStoreTree",
        rank: typing.Optional[int],
        stratum: "HereditaryStratum",
    ) -> None:
        """Insert a new stratum into the store.

        Parameters
        ----------
        rank : typing.Optional[int]
            The position of the stratum being deposited within the sequence of
            strata deposited into the column. Precisely, the number of strata
            that have been deposited before stratum.
        stratum : HereditaryStratum
            The stratum to deposit.
        """
        new_leaf = anytree.AnyNode(stratum=stratum)
        new_leaf.parent = self._leaf
        self._leaf = new_leaf
        self._num_strata_retained += 1

    def GetNumStrataRetained(self: "HereditaryStratumOrderedStoreTree") -> int:
        """How many strata are present in the store?

        May be fewer than the number of strata deposited if deletions have
        occured.
        """
        return self._num_strata_retained

    def GetStratumAtColumnIndex(
        self: "HereditaryStratumOrderedStoreTree",
        index: int,
        # needed for other implementations
        get_rank_at_column_index: typing.Optional[typing.Callable] = None,
    ) -> HereditaryStratum:
        """Get the stratum positioned at index i among retained strata.

        Index order is from most ancient (index 0) to most recent.

        Parameters
        ----------
        ranks : iterator over int
            The ranks that are to be deleted.
        get_column_index_of_rank : callable, optional
            Callable that returns the index position within retained strata of
            the stratum deposited at rank r.
        """
        return next(
            it.islice(
                self._GetAscendingIter(),
                self.GetNumStrataRetained() - 1 - index,
                None,
            )
        ).stratum

    def GetRankAtColumnIndex(
        self: "HereditaryStratumOrderedStoreTree",
        index: int,
    ) -> int:
        """Map from deposition generation to column position.

        What is the deposition rank of the stratum positioned at index i
        among retained strata?
        """
        res_rank = self.GetStratumAtColumnIndex(index).GetDepositionRank()
        assert res_rank is not None
        return res_rank

    def GetColumnIndexOfRank(
        self: "HereditaryStratumOrderedStoreTree",
        rank: int,
    ) -> typing.Optional[int]:
        """Map from column position to deposition generation.

        What is the index position within retained strata of the stratum
        deposited at rank r? Returns None if no stratum with rank r is present
        within the store.
        """
        try:
            return next(
                self.GetNumStrataRetained() - 1 - idx
                for idx, node in enumerate(self._GetAscendingIter())
                if node.stratum.GetDepositionRank() == rank
            )
        except StopIteration:
            return None

    def _do_getrank_DelRanks(
        self: "HereditaryStratumOrderedStoreTree",
        ranks: typing.Iterator[int],
        # deposition ranks are stored in strata
    ) -> None:
        """Provide implementation detail for DelRanks.

        Handles case where deposition ranks are stored in strata.
        """
        # duplicate everything after deepest deletion
        # except other ranks slated for deletion
        pending_node = (
            None  # top of new chain, needs to be attached to a parent
        )

        ascending_iter = self._GetAscendingIter()
        target_ranks = sorted(ranks)
        # pop ranks off back of target_ranks as they're deleted
        while target_ranks:
            cur_node = next(ascending_iter)

            if cur_node.stratum.GetDepositionRank() == target_ranks[-1]:
                # skip over and don't copy node targeted for deletion
                target_ranks.pop()
                self._num_strata_retained -= 1
            else:
                # copy untargeted node and use it as parent for pending node
                new_node = anytree.AnyNode(
                    stratum=cur_node.stratum,
                )
                if pending_node is None:
                    self._leaf = new_node
                else:
                    pending_node.parent = new_node
                pending_node = new_node

        # hook copied content into existing tree
        if pending_node is not None:
            pending_node.parent = next(ascending_iter, None)
        else:
            self._leaf = next(ascending_iter, None)

    def _do_calcrank_DelRanks(
        self: "HereditaryStratumOrderedStoreTree",
        ranks: typing.Iterator[int],
        # deposition ranks are not stored in strata
        get_column_index_of_rank: typing.Callable,
    ) -> None:
        """Provide implementation detail for DelRanks.

        Handles case where deposition ranks are not stored in strata but a
        function to calculate deposition rank from column index is available.
        """
        # duplicate everything after deepest deletion
        # except other ranks slated for deletion

        pending_node = (
            None  # top of new chain, needs to be attached to a parent
        )
        pending_leaf = None  # bottom of new chain
        num_deleted_nodes = 0
        # RE: pending_leaf, num_deleted_nodes
        # get_column_index_of_rank can depend on state of this object
        # so we have to cache changes and apply all at once at the end

        ascending_iter = self._GetAscendingIter()
        ascending_idx = self.GetNumStrataRetained() - 1

        for rank in sorted(ranks, reverse=True):
            target_idx = get_column_index_of_rank(rank)
            assert ascending_idx >= target_idx

            while ascending_idx >= target_idx:
                cur_node = next(ascending_iter)

                if ascending_idx == target_idx:
                    # don't copy node targeted for deletion
                    num_deleted_nodes += 1
                else:
                    # copy untargeted node and use it as parent for pending node
                    new_node = anytree.AnyNode(
                        stratum=cur_node.stratum,
                    )
                    if pending_node is None:
                        pending_leaf = new_node
                    else:
                        pending_node.parent = new_node
                    pending_node = new_node

                # step backward
                ascending_idx -= 1

            assert ascending_idx == target_idx - 1

        # hook copied content into existing tree
        if pending_node is not None:
            pending_node.parent = next(ascending_iter, None)
        else:
            assert pending_leaf is None
            pending_leaf = next(ascending_iter, None)
        # attach self to new copied chain
        if pending_leaf is not None:
            self._leaf = pending_leaf
        # apply cached changes to stratum count
        self._num_strata_retained -= num_deleted_nodes

    def DelRanks(
        self: "HereditaryStratumOrderedStoreTree",
        ranks: typing.Iterator[int],
        # deposition ranks might not be stored in strata
        get_column_index_of_rank: typing.Optional[typing.Callable] = None,
    ) -> None:
        """Purge strata with specified deposition ranks from the store.

        Parameters
        ----------
        ranks : iterator over int
            The ranks that are to be deleted.
        get_column_index_of_rank : callable, optional
            Callable that returns the deposition rank of the stratum positioned at index i among retained strata.
        """
        if get_column_index_of_rank is None:
            self._do_getrank_DelRanks(ranks)
        else:
            self._do_calcrank_DelRanks(ranks, get_column_index_of_rank)

    def IterRetainedRanks(
        self: "HereditaryStratumOrderedStoreTree",
    ) -> typing.Iterator[int]:
        """Iterate over deposition ranks of strata present in the store from
        most ancient to most recent.

        The store may be altered during iteration without iterator
        invalidation, although subsequent updates will not be reflected in the
        iterator.
        """
        # must make copy to prevent invalidation when strata are deleted
        # note, however, that copy is made lazily
        # (only when first item requested)
        ranks = [
            node.stratum.GetDepositionRank()
            for node in self._GetAscendingIter()
        ]
        for rank in reversed(ranks):
            assert rank is not None
            yield rank

    def IterRetainedStrata(
        self: "HereditaryStratumOrderedStoreTree",
    ) -> typing.Iterator[HereditaryStratum]:
        """Iterate over stored strata from most ancient to most recent."""
        yield from reversed(
            [node.stratum for node in self._GetAscendingIter()]
        )

    def _do_reverse_IterRankDifferentiaZip(
        self: "HereditaryStratumOrderedStoreTree",
        # deposition ranks might not be stored in strata
        get_rank_at_column_index: typing.Optional[typing.Callable] = None,
        start_column_index: int = 0,
    ) -> typing.Iterator[typing.Tuple[int, int]]:
        """Iterate over differentia and corresponding depsotion rank.

        Ordered from most recent to most ancient. Implementation detail for
        IterRankDifferentiaZip.
        """
        for reverse_column_idx, node in enumerate(self._GetAscendingIter()):
            column_idx = self.GetNumStrataRetained() - 1 - reverse_column_idx
            if column_idx >= start_column_index:
                rank: int
                if get_rank_at_column_index is None:
                    rank = node.stratum.GetDepositionRank()
                    assert rank is not None
                else:
                    rank = get_rank_at_column_index(column_idx)
                    assert rank is not None
                yield (rank, node.stratum.GetDifferentia())
            else:
                break

    def IterRankDifferentiaZip(
        self: "HereditaryStratumOrderedStoreTree",
        # deposition ranks might not be stored in strata
        get_rank_at_column_index: typing.Optional[typing.Callable] = None,
        start_column_index: int = 0,
    ) -> typing.Iterator[typing.Tuple[int, int]]:
        """Iterate over differentia and corresponding depsotion rank.

        Values yielded as tuples. Guaranteed ordered from most ancient to most
        recent.

        Parameters
        ----------
        get_rank_at_column_index : callable, optional
            Callable that returns the deposition rank of the stratum
            positioned at index i among retained strata.
        start_column_index : callable, optional
            Number of strata to skip over before yielding first result from the
            iterator. Default 0, meaning no strata are skipped over.
        """
        reverse_iter = self._do_reverse_IterRankDifferentiaZip(
            get_rank_at_column_index=get_rank_at_column_index,
            start_column_index=start_column_index,
        )
        reverse_data = [*reverse_iter]
        return reversed(reverse_data)

    def Clone(
        self: "HereditaryStratumOrderedStoreTree",
    ) -> "HereditaryStratumOrderedStoreTree":
        """Create an independent copy of the store.

        Returned copy contains identical data but may be freely altered without
        affecting data within this store.
        """
        # shallow copy
        res = copy(self)
        # must create independent leaf
        if self._leaf is not None:
            res._leaf = anytree.AnyNode(
                stratum=self._leaf.stratum,
            )
            res._leaf.parent = self._leaf.parent
        return res
