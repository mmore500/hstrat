"""Alias of `hstrat.dataframe.build_trie.surface_unpack_reconstruct` CLI."""

from .._auxiliary_lib import begin_prod_logging
from .build_trie.surface_unpack_reconstruct import (  # noqa: F401
    _create_parser,
    _main,
)

if __name__ == "__main__":
    begin_prod_logging()
    _main("spawn")
