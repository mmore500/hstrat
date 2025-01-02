import typing

import pandas as pd
import polars as pl

from ...._auxiliary_lib import anytree_iterative_deepcopy
from .._impl import TrieInnerNode
from ._detail import TriePostprocessorBase


class NopTriePostprocessor(TriePostprocessorBase):
    """Functor for nop trie postprocess."""

    def __call__(
        self: "NopTriePostprocessor",
        trie: typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame],
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame]:
        """Apply postprocess functors to the input trie.

        Parameters
        ----------
        trie : TrieInnerNode or pd.DataFrame or pl.DataFrame
            The input trie to be postprocessed.
        p_differentia_collision : float
            Probability of a randomly-generated differentia matching an
            existing differentia.

            Not used in the current implementation.
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?

            If False, a deep copy of the input trie is made.
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress.

        Returns
        -------
        TrieInnerNode or pd.DataFrame or pl.DataFrame
            The postprocessed trie, identical to input.
        """
        if isinstance(trie, TrieInnerNode):
            if not mutate:
                trie = anytree_iterative_deepcopy(
                    trie, progress_wrap=progress_wrap
                )
        elif isinstance(trie, pd.DataFrame):
            if not mutate:
                trie = trie.copy()
        elif isinstance(trie, pl.DataFrame):
            if not mutate:
                trie = trie.clone()
        else:
            raise TypeError
        return trie
