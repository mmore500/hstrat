import copy
import random
import typing

import anytree
import opytional as opyt

from ...._auxiliary_lib import generate_n, render_to_base64url
from ._TrieLeafNode import TrieLeafNode


class TrieInnerNode(anytree.NodeMixin):
    """Inner node of a trie (a.k.a. prefix tree) of differentia
    sequences of hereditary stratigraphic artifacts within a population.
    Each inner node represents the hypothesized origination of a particular
    allele (i.e., differentia at a particular rank).

    Note that more than one` TrieInnerNode` representing a particular
    rank/differentia combination may be present. This is only the case when the
    colliding alleles are known to have independent origins due to previous
    disparities in the phylogenetic record.

    Only `TrieLeafNode` instances will occupy leaf node positions in the trie
    structure. Each `TrieLeafNode` represents a single member of the extant
    artifact population. An instance of `TrieInnerNode` may have child nodes of
    both types.
    """

    _rank: int  # rank of represented allele
    _differentia: int  # differentia of represented allele
    _tiebreaker: int  # random 128-bit integer used to break ties.

    def __init__(
        self: "TrieInnerNode",
        rank: typing.Optional[int] = None,
        differentia: typing.Optional[int] = None,
        parent: typing.Optional["TrieInnerNode"] = None,
    ) -> None:
        """Initialize a `TrieInnerNode` instance.

        Parameters
        ----------
        rank : int, optional
            The rank of the node, or None for shim "ancestor of all geneses" root node.

            Pass None for root node, int otherwise
        differentia : int, optional
            The fingerprint or differentia of the node, or None for shim
            "ancestor of all geneses" root node.
        parent : int, optional
            The parent node, or None for shim "ancestor of all geneses" root
            node.
        """
        self.parent = parent
        self._rank = rank
        self._differentia = differentia
        assert (self._rank is None) == (self._differentia is None)
        self._tiebreaker = random.getrandbits(128)  # uuid standard 128 bits

    def IsAnOriginationOfAllele(
        self: "TrieInnerNode",
        rank: int,
        differentia: int,
    ) -> bool:
        """Checks if the node represents an origination of a given allele."""
        return self._rank == rank and self._differentia == differentia

    def FindOriginationsOfAllele(
        self: "TrieInnerNode",
        rank: int,
        differentia: int,
    ) -> typing.Iterator["TrieInnerNode"]:
        """Searches subtree to find all possible `TrieInnerNodes` representing
        an origination of the specified `rank`-`differentia` allele."""
        assert rank is not None
        assert differentia is not None
        # note: assert handles root case
        assert (self._differentia is None) == (self._rank is None)

        search_stack = [self]
        while search_stack:
            current_node = search_stack.pop()

            # handle root node case
            if current_node._rank is None:
                search_stack.extend(current_node.inner_children)
            # If the current node matches the rank and differentia, yield it
            elif current_node.IsAnOriginationOfAllele(rank, differentia):
                yield current_node
            # If the target allele's rank is deeper than the current node,
            # keep searching
            elif rank > current_node._rank:
                search_stack.extend(current_node.inner_children)

    def GetDeepestCongruousAlleleOrigination(
        self: "TrieInnerNode",
        taxon_allele_iter: typing.Iterator[typing.Tuple[int, int]],
    ) -> (
        typing.Tuple["TrieInnerNode", typing.Iterator[typing.Tuple[int, int]]]
    ):
        """Descends the subtrie to retrieve the deepest prefix consistent with
        the hereditary stratigraphic record of a query taxon.

        In the case where more than one possible originations are found for an
        allele, all will be searched recursively for further matches with the
        next alleles in the focal taxon's hereditary stratigraphic record.
        (This scenario occurs when the focal taxon has discarded a strata that
        differentiates subsequently colliding alleles among earlier taxa).
        Nodes' `_tiebreaker` fields determinstically resolve any ambiguities
        for the deepest consistent prefix that may aries in such cases.

        Parameters
        ----------
        taxon_allele_iter : typing.Iterator[typing.Tuple[int, int]]
            An iterator over the taxon alleles (rank/differentia pairs) in rank-
            ascending order.

            Must be copyable.

        Returns
        -------
        typing.Tuple["TrieInnerNode", typing.Iterator[typing.Tuple[int, int]]]
            A tuple containing the retrieved deepest prefix tree match and an
            iterator over the taxon alleles remaining past the retrieved allele.
        """
        # iterator must be copyable
        assert [*copy.copy(taxon_allele_iter)] == [
            *copy.copy(taxon_allele_iter)
        ]

        node_stack = [self]
        allele_origination_stack = [taxon_allele_iter]
        deepest_origination = self
        deepest_taxon_allele_iter = copy.copy(taxon_allele_iter)
        while True:

            candidate_origination = node_stack.pop()
            taxon_allele_iter = allele_origination_stack.pop()

            # Update the deepest origination if the candidate is deeper
            if (
                opyt.or_value(candidate_origination._rank, -1),
                candidate_origination._tiebreaker,
            ) > (
                opyt.or_value(deepest_origination._rank, -1),
                deepest_origination._tiebreaker,
            ):
                deepest_origination = candidate_origination
                deepest_taxon_allele_iter = copy.copy(taxon_allele_iter)

            # If taxon has susbsequent allele, search its origination
            next_allele = next(taxon_allele_iter, None)
            if next_allele is not None:
                node_stack.extend(
                    candidate_origination.FindOriginationsOfAllele(
                        *next_allele
                    )
                )
                allele_origination_stack.extend(
                    generate_n(
                        lambda: copy.copy(taxon_allele_iter),
                        len(node_stack) - len(allele_origination_stack),
                    )
                )

            assert len(node_stack) == len(allele_origination_stack)

            if not node_stack:  # no more nodes to explore
                break

        return deepest_origination, deepest_taxon_allele_iter

    def InsertTaxon(
        self: "TrieInnerNode",
        taxon_label: str,
        taxon_allele_iter: typing.Iterator[typing.Tuple[int, int]],
    ) -> TrieLeafNode:
        """Inserts a taxon into the trie, ultimately resulting in the creation
        of an additional `TrieLeafNode` leaf and --- if necessary --- a
        unifurcating chain of `TrieInnerNode`'s subtending it.

        Parameters
        ----------
        taxon_label : str
            The label of the taxon to be inserted.
        taxon_allele_iter : typing.Iterator[typing.Tuple[int, int]]
            An iterator over the taxon's remaining allele sequence that has not
            yet been accounted for thus deep into the trie.

        Notes
        -----
        Should only be called on the node corresponding to the deepest congrous
        allele origination found via `GetDeepestCongruousAlleleOrigination`.
        However, may be called on the trie root node when the entire artifact
        population has identical deposition counts. (Because, given a
        deterministic stratum retention strategy, insertion is greatly
        simplified because no colliding allele originations can arise due to
        the impossibility of preceding divergences not retained by the taxon
        being inserted.)

        Returns
        -------
        TrieLeafNode
            The leaf node representing the inserted taxon.
        """
        cur_node = self
        for next_rank, next_differentia in taxon_allele_iter:
            assert next_rank is not None
            assert next_differentia is not None
            for child in cur_node.inner_children:
                # check immediate children for next allele
                #
                # common allele origination trace is for special condition
                # optimization where GetDeepestCongruousAlleleOrigination
                # isn't needed
                if child.IsAnOriginationOfAllele(next_rank, next_differentia):
                    cur_node = child
                    break
            else:
                # if no congruent node exists, create a new TrieInnerNode
                cur_node = TrieInnerNode(
                    next_rank, next_differentia, parent=cur_node
                )

        # create a TrieLeafNode representing the inserted taxon
        return TrieLeafNode(parent=cur_node, taxon_label=taxon_label)

    @property
    def taxon_label(self: "TrieInnerNode") -> str:
        """Programatically-generated unique identifier for internal node,
        intended to translate into a unique label for internal taxa after
        conversion to a phylogenetic reconstruction."""
        if self.parent is None:
            return "Root"
        else:
            # numpy ints cause indexing errors; convert to native int
            # uid field necessary to distinguish colliding allele originations
            return f"""Inner+r={self._rank}+d={
                render_to_base64url(int(self._differentia))
            }+uid={
                render_to_base64url(int(self._tiebreaker))
            }"""

    @property
    def taxon(self: "TrieInnerNode") -> str:
        """Alias for taxon_label."""
        return self.taxon_label

    @property
    def rank(self: "TrieInnerNode") -> int:
        return opyt.or_value(self._rank, 0)

    @property
    def inner_children(
        self: "TrieInnerNode",
    ) -> typing.Iterator["TrieInnerNode"]:
        """Returns iterator over non-leaf child nodes."""
        return filter(
            lambda child_: isinstance(child_, TrieInnerNode),
            self.children,
        )

    @property
    def outer_children(
        self: "TrieInnerNode",
    ) -> typing.Iterator["TrieLeafNode"]:
        """Returns iterator over leaf child nodes."""
        return filter(
            lambda child_: isinstance(child_, TrieLeafNode),
            self.children,
        )

    def __repr__(self: "TrieInnerNode") -> str:
        return f"""(rank {
            self._rank
        }, diff {
            self._differentia
        }) @ {
            render_to_base64url(id(self) % 8192)
        }"""
