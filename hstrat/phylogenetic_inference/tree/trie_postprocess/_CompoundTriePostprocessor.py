import typing

from ...._auxiliary_lib import anytree_iterative_deepcopy
from .._impl import TrieInnerNode


class CompoundTriePostprocessor:

    _postprocessors: typing.Iterable[typing.Callable]

    def __init__(
        self: "CompoundTriePostprocessor",
        postprocessors: typing.Iterable[typing.Callable],
    ) -> None:
        self._postprocessors = postprocessors

    def __call__(
        self: "CompoundTriePostprocessor",
        trie: TrieInnerNode,
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> TrieInnerNode:
        """Apply stored postprocessors in sequence.

        Parameters
        ----------
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?

        Returns
        -------
        TrieInnerNode
            The postprocessed trie.
        """
        if not mutate:
            trie = anytree_iterative_deepcopy(
                trie, progress_wrap=progress_wrap
            )

        for postprocessor in self._postprocessors:
            trie = postprocessor(
                trie=trie,
                p_differentia_collision=p_differentia_collision,
                mutate=True,
                progress_wrap=progress_wrap,
            )

        return trie
