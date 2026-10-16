import argparse

from joinem._dataframe_cli import _add_parser_base

from ..._auxiliary_lib import (
    add_bool_arg,
    format_cli_description,
    get_hstrat_version,
)


def create_surface_build_tree_cli_parser(
    raw_description: str,
    dfcli_module: str,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        allow_abbrev=False,
        description=format_cli_description(raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_parser_base(
        parser=parser,
        dfcli_module=dfcli_module,
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "--collapse-unif-freq",
        type=int,
        default=1,
        help="How often should dropped unifurcations be garbage collected?",
    )
    parser.add_argument(
        "--check-trie-invariant-freq",
        type=int,
        default=0,
        help=(
            "How often should trie invariant checks be run? "
            "Set to 0 to disable (default). "
            "Set to n > 0 to check every n slices."
        ),
    )
    add_bool_arg(
        parser,
        "check-trie-invariant-after-collapse-unif",
        default=False,
        help=(
            "Should trie invariant checks also be run after collapse "
            "unifurcations? Default is False (checks run before collapse only)."
        ),
    )
    parser.add_argument(
        "--exploded-slice-size",
        type=int,
        default=1_000_000,
        help="Number of rows to process at once. Low values reduce memory use.",
    )
    parser.add_argument(
        "--mp-pool-size",
        type=int,
        default=1,
        help=(
            "Number of worker processes for exploding slices in parallel. "
            "Default 1 (single producer process)."
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
    parser.add_argument(
        "--trie-postprocessor",
        type=str,
        default="hstrat.NopTriePostprocessor()",
        help=(
            "Functor to apply to finalize postprocessed phylogeny. "
            "Postprocessors are available to estimate taxon `origin_time`, "
            "apply topological corrections for systematic overestimation of "
            "relatedness, etc. "
            "Will be `eval`-ed as Python code before use. "
            "Must support Pandas dataframe input."
        ),
    )
    parser.add_argument(
        "--pa-source-type",
        type=str,
        default="memory_map",
        help=(
            "PyArrow type to use for exploded chunks "
            """(i.e., "memory_map" or "OSFile")."""
        ),
    )
    parser.add_argument(
        "--shuffle-over-same-T-seed",
        type=int,
        default=None,
        help=(
            "If set, shuffle rows within same-dstream_T groups after "
            "sorting but before exploding. Value is the random seed."
        ),
    )
    add_bool_arg(
        parser,
        "drop-dstream-metadata",
        default=None,
        help=(
            "Drop all dstream/downstream columns from the output? "
            "Omit for default behavior (drop some metadata). "
            "Use --no-drop-dstream-metadata to retain."
        ),
    )

    return parser
