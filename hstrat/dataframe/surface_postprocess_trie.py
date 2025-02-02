import argparse
import functools
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli

from .. import hstrat
from .._auxiliary_lib import (
    configure_prod_logging,
    format_cli_description,
    get_hstrat_version,
    log_context_duration,
)
from ._surface_postprocess_trie import surface_postprocess_trie

raw_message = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Second component of raw interface to tree reconstruction for surface-based genome annotations.
Reads raw phylogeny reconstruction data from reconstruction in tabular data file(s) and writes postprocessed phylogeny data to output file in alife standard format.


End-users are recommended to prefer `hstrat.dataframe.surface_build_tree` for end-to-end processing.
Surface-only implementation --- not compatible with HereditaryStratigraphicColumn genome annotations.


Input Schema: Required Columns
==============================
'id' : integer
    - Unique identifier for each taxon (RE alife standard format).
'ancestor_id' : integer
    - Unique identifier for ancestor taxon  (RE alife standard format).
'hstrat_rank' : integer
    - Num generations elapsed for ancestral differentia.
    - Corresponds to `dstream_Tbar` for inner nodes.
    - Corresponds `dstream_T` - 1 for leaf nodes
'hstrat_differentia_bitwidth' : integer
    - Size of annotation differentiae, in bits.
    - Corresponds to `dstream_value_bitwidth`.
'dstream_S' : integer
    - Capacity of dstream buffer used for hstrat surface, in number
        of data items (i.e., differentia values).


If required columns are not included in raw data, they must be created through CLI flags.
For example,
    --with-column 'pl.lit(16).alias("dstream_S")'


Input Schema: Optional Columns
==============================
'dstream_data_id' : integer
    Unique identifier for each taxon from source genome dataframe.


Additional user-provided columns will be forwarded to phylogeny output.
For these columns, output rows for tip nodes are assigned values from corresponding genome row in original data.


Output Schema: Required Columns
===============================
'id' : integer
    Unique identifier for each taxon (RE alife standard format).
    Will be reassigned for contiguity and may differ from input.

'ancestor_id' : integer
    Unique identifier for ancestor taxon (RE alife standard format).

'hstrat_rank_from_t0' : integer
    - Num generations elapsed for ancestral differentia.
    - Corresponds to `dstream_Tbar` - `dstream_S` for inner nodes.
    - Corresponds `dstream_T` - 1 - `dstream_S` for leaf nodes


Output Schema: Optional Columns
===============================
'origin_time' : floating point or integer
    Estimated num generations elapsed from founding ancestor.
    Value depends on the trie postprocessor used.

Additional user-defined columns will be forwarded from the input DataFrame.
Note that the alife-standard `ancestor_list` column is not included in output schema.


See Also
========
-m hstrat.dataframe.surface_surface_unpack_reconstruct :
    Creates raw phylogeny data postprocessed here.

-m hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col :
    Adds alife-standard `ancestor_list` column to phylogeny data.


Additional Notes
================
Behind the scenes, the following postprocessing steps occur:
1. Trunk nodes with rank less than `dstream_S` are deleted.

2. Internal unifurcations are collapsed.

3. Taxon `id` values are reassigned.

4. Supplied `trie_postprocessor` functor is applied.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(raw_message),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_parser_base(
        parser=parser,
        dfcli_module="hstrat.dataframe.surface_postprocess_trie",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "--trie-postprocessor",
        type=str,
        default="hstrat.NopTriePostprocessor()",
        help=(
            "Functor to apply to finalize postprocessed phylogeny. "
            "Postprocessors are available to estimate taxon `origin_time`, "
            "apply topological corrections for systematic overestimation of "
            "relatedness, etc. "
            "Will be `eval`-ed as Python code before use."
            "Must support Pandas dataframe input."
        ),
    )
    parser.add_argument(
        "--delete-trunk",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Should trunk nodes with rank less than `dstream_S` be deleted? "
            "Trunk deletion accounts for 'dummy' strata added to fill hstrat "
            "surface for founding ancestor(s), by segregating subtrees with "
            "distinct founding strata into independent trees."
        ),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    logging.info(
        "instantiating trie postprocess functor: "
        f"`{args.trie_postprocessor}`",
    )
    trie_postprocessor = eval(args.trie_postprocessor, {"hstrat": hstrat})

    with log_context_duration(
        "hstrat.dataframe.surface_postprocess_trie", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=functools.partial(
                surface_postprocess_trie,
                delete_trunk=args.delete_trunk,
                trie_postprocessor=trie_postprocessor,
            ),
        )
