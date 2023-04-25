import typing

from ...._auxiliary_lib import anytree_iterative_deepcopy
from .._impl import TrieInnerNode


class CompoundTriePostprocessor:
    """Functor to sequentially apply multiple trie postprocessors.

    Allows for the combination and sequential application of multiple trie
    postprocessors.
    """

    _postprocessors: typing.Iterable[typing.Callable]

    def __init__(
        self: "CompoundTriePostprocessor",
        postprocessors: typing.Iterable[typing.Callable],
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        postprocessors : typing.Iterable[typing.Callable]
            The sequence of postprocess functors to be applied.
        """
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
        trie : TrieInnerNode
            The input trie to be postprocessed.
        p_differentia_collision : float
            Probability of a randomly-generated differentia matching an
            existing differentia.

            Forwarded to the postprocess functors.
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress.

        Returns
        -------
        TrieInnerNode
            The postprocessed trie after applying all stored postprocessors.
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
