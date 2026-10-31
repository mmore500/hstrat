import functools
import logging
import os

import joinem
from joinem._dataframe_cli import _run_dataframe_cli

from ... import hstrat
from ..._auxiliary_lib import (
    begin_prod_logging,
    get_hstrat_version,
    log_context_duration,
)
from .._impl import create_surface_build_tree_cli_parser
from ._surface_build_tree import surface_build_tree

raw_message = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

End-to-end interface to tree reconstruction for surface-based genome annotations, by average-linkage UPGMA over tree-free pairwise origin-time estimates, scaffolded by a reconstructed trie.
Reads raw hex genome data from tabular data file(s) and writes postprocessed phylogeny data to output file in alife standard format.


Surface-only implementation --- not compatible with HereditaryStratigraphicColumn genome annotations.


Input Schema: Required Columns
==============================
'data_hex' : string
    Raw genome data, with serialized dstream buffer and counter.
    Represented as a hexadecimal string.

'dstream_algo' : string or categorical
    Name of downstream curation algorithm used (e.g., 'dstream.steady_algo').

'dstream_storage_bitoffset' : integer
    Position of dstream buffer field in 'data_hex'.

'dstream_storage_bitwidth' : integer
    Size of dstream buffer field in 'data_hex'.

'dstream_T_bitoffset' : integer
    Position of dstream counter field ("rank") in 'data_hex'.

'dstream_T_bitwidth' : integer
    Size of dstream counter field in 'data_hex'.

'dstream_S' : integer
    Capacity of dstream buffer, in number of data items (i.e., num differentia stored per annotation).


If required columns are not included in raw data, they must be created through CLI flags.
For example,
    --with-column 'pl.lit("dstream.tilted_algo").alias("dstream_algo").cast(pl.Categorical)'
    --with-column 'pl.lit("genome_string").alias("data_hex")'


To work with genome data in raw binary format (e.g., pl.Binary),
    --with-column 'pl.col("data_bin").bin.encode("hex").alias("data_hex")'


Additional user-provided columns will be forwarded to phylogeny output.
For these columns, output rows for tip nodes are assigned values from corresponding genome row in original data.
Internal tree nodes will take null values in user-provided columns.


Output Schema: Required Columns
===============================
'id' : integer
    Unique identifier for each taxon (RE alife standard format).
    Will be reassigned for contiguity and may differ from input.

'ancestor_id' : integer
    Unique identifier for ancestor taxon (RE alife standard format).

'origin_time' : floating point
    Estimated num generations elapsed from founding ancestor.
    Mean pairwise origin-time estimate between children's tips, for inner nodes.
    Corresponds to `dstream_T` - 1 - `dstream_S` for leaf nodes.
    May be reassigned by the trie postprocessor.

'dstream_data_id' : integer
    Identifier of genome, for leaf nodes; null for inner nodes.

The tree is binary, with a single root.


Output Schema: Optional Columns
===============================
Additional user-defined columns will be forwarded from the input DataFrame onto leaf nodes.
Note that the alife-standard `ancestor_list` column is not included in output schema.


See Also
========
-m hstrat.dataframe.build_trie.surface_build_tree :
    Trie-based tree reconstruction.

-m hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col :
    Adds alife-standard `ancestor_list` column to phylogeny data.
"""


def _main(mp_context: str) -> None:
    parser = create_surface_build_tree_cli_parser(
        raw_description=raw_message,
        dfcli_module="hstrat.dataframe.build_trie_upgma.surface_build_tree",
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=5,
        help="Number of closest candidate neighbors kept per genome.",
    )
    parser.add_argument(
        "--candidate-pool-size",
        type=int,
        default=10,
        help="Number of trie-adjacent genomes evaluated per genome.",
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=64,
        help="Number of sampled tip pairs per large-cluster linkage value.",
    )
    parser.add_argument(
        "--direct-max",
        type=int,
        default=64,
        help="Compute linkage exactly when product of cluster sizes is at most this.",
    )
    parser.add_argument(
        "--sampling-seed",
        type=int,
        default=1,
        help="Random seed for sampled linkage values.",
    )
    args, __ = parser.parse_known_args()

    logging.info(
        "instantiating trie postprocess functor: "
        f"`{args.trie_postprocessor}`",
    )
    trie_postprocessor = eval(args.trie_postprocessor, {"hstrat": hstrat})

    with log_context_duration(
        "hstrat.dataframe.build_trie_upgma.surface_build_tree", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=functools.partial(
                surface_build_tree,
                collapse_unif_freq=args.collapse_unif_freq,
                drop_dstream_metadata=args.drop_dstream_metadata,
                exploded_slice_size=args.exploded_slice_size,
                mp_context=mp_context,
                mp_pool_size=args.mp_pool_size,
                pa_source_type=args.pa_source_type,
                num_candidates=args.num_candidates,
                candidate_pool_size=args.candidate_pool_size,
                num_samples=args.num_samples,
                direct_max=args.direct_max,
                sampling_seed=args.sampling_seed,
                trie_postprocessor=trie_postprocessor,
            ),
        )


if __name__ == "__main__":
    begin_prod_logging()

    _main("spawn")
