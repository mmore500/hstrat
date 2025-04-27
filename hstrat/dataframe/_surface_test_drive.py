from downstream import dstream, dsurf
import polars as pl

from .._auxiliary_lib import alifestd_mark_leaves
from ..genome_instrumentation import HereditaryStratigraphicSurface
from ..serialization import surf_to_hex
from ..test_drive import descend_template_phylogeny_alifestd


def surface_test_drive(
    df: pl.LazyFrame,
    *,
    dstream_algo: str,
    dstream_S: int,
    dstream_T_bitwidth: int = 32,
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
            - 'dstream_storage_bitoffset' : pl.UInt32
                - Position of dstream buffer field in 'data_hex'.
            - 'dstream_storage_bitwidth' : pl.UInt32
                - Size of dstream buffer field in 'data_hex'.
            - 'dstream_T_bitoffset' : pl.UInt32
                - Position of dstream counter field in 'data_hex'.
            - 'dstream_T_bitwidth' : pl.UInt32
                - Size of dstream counter field in 'data_hex'.
            - 'dstream_S' : pl.Uint32
                - Capacity of dstream buffer, in number of data items.
            - 'origin_time' : pl.UInt64
                - Number of generations elapsed since the founding ancestor.
            - 'td_source_id' : pl.UInt64
                - Corresponding taxon identifier in source phylogeny.

        Additional user-defined columns will be forwarded from the input
        DataFrame.

    Notes
    -----
    - Input columns "id", "ancestor_id", and "ancestor_list" are not forwarded
      to output, to avoid conflicts with the output schema for subsequent
      phylogeny reconstruction.
    """
    df = df.lazy().collect()

    ancestor_instrument = HereditaryStratigraphicSurface(
        dstream_surface=dsurf.Surface(
            algo=eval(dstream_algo, {"dstream": dstream}),
            storage=dstream_S,
        ),
        predeposit_strata=0,
        stratum_differentia_bit_width=stratum_differentia_bit_width,
    )
    df_pd = df.to_pandas()
    if "extant" not in df_pd.columns:
        df_pd = alifestd_mark_leaves(df_pd, mutate=True)
        df_pd["extant"] = df_pd["is_leaf"].values

    extant_ids = df_pd.loc[df_pd["extant"].values, "id"].values
    surfaces = descend_template_phylogeny_alifestd(
        df_pd,
        extant_ids=extant_ids,
        seed_instrument=ancestor_instrument,
    )

    data = {
        "data_hex": [surf_to_hex(surf) for surf in surfaces],
        "dstream_algo": dstream_algo,
        "dstream_storage_bitwidth": dstream_S * stratum_differentia_bit_width,
        "dstream_storage_bitoffset": dstream_T_bitwidth,
        "dstream_T_bitwidth": dstream_T_bitwidth,
        "dstream_T_bitoffset": 0,
        "dstream_S": dstream_S,
        "origin_time": [surf.GetNextRank() for surf in surfaces],
        "td_source_id": extant_ids,
    }
    schema = {
        "data_hex": pl.Utf8,
        "dstream_algo": pl.Categorical,
        "dstream_storage_bitwidth": pl.UInt32,
        "dstream_storage_bitoffset": pl.UInt32,
        "dstream_T_bitwidth": pl.UInt32,
        "dstream_T_bitoffset": pl.UInt32,
        "dstream_S": pl.UInt32,
        "origin_time": pl.UInt64,
        "td_source_id": pl.UInt64,
    }
    return pl.concat(
        (
            pl.DataFrame(data, schema=schema),
            df.select(
                pl.exclude("id", "ancestor_id", "ancestor_list", *data.keys()),
            ).filter(df_pd["extant"].values),
        ),
        how="horizontal",
    )
