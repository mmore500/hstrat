import typing

import pandas as pd
import polars as pl

from .._impl import TrieInnerNode
from ._NopTriePostprocessor import NopTriePostprocessor
from ._detail import TriePostprocessorBase


class CompoundTriePostprocessor(TriePostprocessorBase):
    """Functor to sequentially apply multiple trie postprocessors.

    Allows for the combination and sequential application of multiple trie
    postprocessors.
    """

    _postprocessors: typing.Iterable[typing.Callable]

    def __init__(
        self: "CompoundTriePostprocessor",
        postprocessors: typing.Iterable[TriePostprocessorBase],
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        postprocessors : typing.Iterable[TriePostprocessorBase]
            The sequence of postprocess functors to be applied.
        """
        self._postprocessors = postprocessors
        if not postprocessors:
            # ensure copy made if mutate is False
            self._postprocessors.append(NopTriePostprocessor())

    def __call__(
        self: "CompoundTriePostprocessor",
        trie: typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame],
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame]:
        """Apply stored postprocessors in sequence.

        Parameters
        ----------
        trie : TrieInnerNode or pd.DataFrame or pl.DataFrame
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
        TrieInnerNode or pd.DataFrame or pl.DataFrame
            The postprocessed trie after applying all stored postprocessors.
        """
        for i, postprocessor in enumerate(self._postprocessors):
            trie = postprocessor(
                trie=trie,
                p_differentia_collision=p_differentia_collision,
                mutate=i > 0 or mutate,
                progress_wrap=progress_wrap,
            )

        return trie
