from downstream import dstream, dsurf
import polars as pl

from .. import hstrat
from .._auxiliary_lib import alifestd_try_add_ancestor_list_col
from ..genome_instrumentation import HereditaryStratigraphicSurface


def surface_test_drive(
    df: pl.LazyFrame,
    *,
    dstream_algo: str,
    dstream_S: int,
    stratum_differentia_bit_width: int,
) -> pl.DataFrame:
    """Reads alife standard phylogeny dataframe to create a population of
    hstrat surface annotations corresponding to the phylogeny tips, "as-if"
    they had evolved according to the provided phylogeny history.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame containing alife standard phylogeny with required
        columns, one row per taxon.

        Note that the alife-standard `ancestor_list` column is not required.

        Required schema:
            - 'id' : pl.UInt64
                - Taxon identifier.
            - 'ancestor_id' : pl.UInt64
                - Taxon identifier of ancestor.
                - Own 'id' if root.

        Optional schema:
            - 'origin_time' : pl.UInt64
                - Number of generations elapsed from ancestor.
                - Determines branch lengths.
                - Otherwise, all branches are assumed to be length 1.
            - 'extant' : pl.Boolean
                - Should an entry corresponding to this phylogeny taxon be
                  included in the output population?
                - Otherwise, all tips are considered extant and all inner nodes
                  are not.
            - Additional user-defined columns will be forwarded to the output
              DataFrame.

    dstream_algo : str
        Name of downstream curation algorithm to use.

    dstream_S : int
        Capacity of annotation dstream buffer, in number of data items.

    stratum_differentia_bit_width : int
        The bit width of the generated differentia.

    Returns
    -------
    pl.DataFrame
        The output DataFrame containing generated hstrat surface annotations.

        Required schema:
            - 'data_hex' : pl.String
                - Raw genome data, with serialized dstream buffer and counter.
                - Represented as a hexadecimal string.
            - 'dstream_algo' : pl.Categorical
                - Name of downstream curation algorithm used.
                - e.g., 'dstream.steady_algo'
            - 'dstream_storage_bitoffset' : pl.UInt64
                - Position of dstream buffer field in 'data_hex'.
            - 'dstream_storage_bitwidth' : pl.UInt64
                - Size of dstream buffer field in 'data_hex'.
            - 'dstream_T_bitoffset' : pl.UInt64
                - Position of dstream counter field in 'data_hex'.
            - 'dstream_T_bitwidth' : pl.UInt64
                - Size of dstream counter field in 'data_hex'.
            - 'dstream_S' : pl.Uint32
                - Capacity of dstream buffer, in number of data items.
            - 'origin_time' : pl.UInt64
                - Number of generations elapsed since the founding ancestor.

        Additional user-defined columns will be forwarded from the input
        DataFrame.
    """
    surfaces = hstrat.descend_template_phylogeny_alifestd(
        df.lazy().collect().to_pandas(),
        HereditaryStratigraphicSurface(
            dsurf.Surface(
                eval(dstream_algo, {"dstream": dstream}),
                dstream_S,
            )
        ),
    )

    dstream_storage_bitwidth = dstream_S * stratum_differentia_bit_width
    dstream_storage_bitoffset = 32
    dstream_T_bitwidth = 32
    dstream_T_bitoffset = 0
    hex_encodings = [surf.to_hex() for surf in surfaces]
    origin_times = [surf.GetNumStrataDeposited() - surf.S for surf in surfaces]

    nrow = len(surfaces)
    return pl.DataFrame(
        {
            "origin_time": origin_times,
            "data_hex": hex_encodings,
            "dstream_storage_bitwidth": [dstream_storage_bitwidth] * nrow,
            "dstream_storage_bitoffset": [dstream_storage_bitoffset] * nrow,
            "dstream_T_bitwidth": [dstream_T_bitwidth] * nrow,
            "dstream_T_bitoffset": [dstream_T_bitoffset] * nrow,
            "dstream_S": [dstream_S] * nrow,
            "dstream_algo": [dstream_algo] * nrow,
        },
    )
