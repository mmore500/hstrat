import typing

import polars as pl

from ._detail import TriePostprocessorBase


class PipeCallablePostprocessor(TriePostprocessorBase):
    """Functor to apply a generic callable to the trie, as
    `polars.DataFrame.pipe`.

    Notes
    -----
    Only polars dataframe tries are supported (e.g., via
    `surface_postprocess_trie`).

    Examples
    --------
    >>> hstrat.dataframe.surface_build_tree(  # doctest: +SKIP
    ...     df,
    ...     trie_postprocessor=hstrat.PipeCallablePostprocessor(
    ...         lambda trie: trie.with_columns(foo=pl.lit("bar")),
    ...     ),
    ... )

    or, from the command line,
    `--trie-postprocessor 'hstrat.PipeCallablePostprocessor(lambda trie: trie.with_columns(foo=pl.lit("bar")))'`.
    """

    _function: typing.Callable  # applied to trie, returning trie
    _args: tuple  # additional positional arguments for function
    _kwargs: dict  # additional keyword arguments for function

    def __init__(
        self: "PipeCallablePostprocessor",
        function: typing.Callable[..., pl.DataFrame],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        function : Callable
            Callable taking the trie as its first argument, followed by
            `args` and `kwargs`, and returning the postprocessed trie.
        *args
            Additional positional arguments passed to `function`.
        **kwargs
            Additional keyword arguments passed to `function`.
        """
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def __call__(
        self: "PipeCallablePostprocessor",
        trie: pl.DataFrame,
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> pl.DataFrame:
        """Apply callable to trie.

        Parameters
        ----------
        trie : pl.DataFrame
            The input trie to be postprocessed.

            Only polars dataframe tries are supported; other types raise
            `NotImplementedError`.
        p_differentia_collision : float
            Probability of a randomly-generated differentia matching an
            existing differentia.

            Not used.
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress.

            Not used.

        Returns
        -------
        pl.DataFrame
            The trie returned by the callable.
        """
        if not isinstance(trie, pl.DataFrame):
            raise NotImplementedError(
                f"{type(trie)} tries are not supported; use polars "
                "dataframe tries (e.g., surface_postprocess_trie)",
            )
        if not mutate:
            trie = trie.clone()
        return trie.pipe(self._function, *self._args, **self._kwargs)
