"""Alias of `hstrat.dataframe.build_trie.surface_test_drive` CLI."""

from .._auxiliary_lib import begin_prod_logging
from .build_trie.surface_test_drive import _main

if __name__ == "__main__":
    begin_prod_logging()
    _main()
