import typing

from downstream import dstream
import numpy as np
import pandas as pd

from .._auxiliary_lib import numpy_fromiter_polyfill
from ..frozen_instrumentation import (
    HereditaryStratigraphicAssemblage,
    HereditaryStratigraphicSpecimen,
)
from ._surf_from_hex import surf_from_hex

# columns required to deserialize surfaces from data_hex
_deserialization_columns = (
    "data_hex",
    "dstream_algo",
    "dstream_storage_bitoffset",
    "dstream_storage_bitwidth",
    "dstream_T_bitoffset",
    "dstream_T_bitwidth",
    "dstream_S",
)


def _surf_to_specimen(surface):
    """Convert a HereditaryStratigraphicSurface to a
    HereditaryStratigraphicSpecimen.

    Unlike col_to_specimen, handles surfaces with negative ranks
    (pre-initialization strata) by using signed integer dtypes.
    """
    differentia = numpy_fromiter_polyfill(
        surface.IterRetainedDifferentia(),
        dtype=np.min_scalar_type(
            2 ** surface.GetStratumDifferentiaBitWidth() - 1
        ),
    )
    ranks = numpy_fromiter_polyfill(
        surface.IterRetainedRanks(),
        dtype=np.int64,
    )

    return HereditaryStratigraphicSpecimen(
        stratum_differentia_series=pd.Series(data=differentia, index=ranks),
        stratum_differentia_bit_width=(
            surface.GetStratumDifferentiaBitWidth()
        ),
    )


def assemblage_from_dstream_df(
    df: pd.DataFrame,
    progress_wrap: typing.Callable = lambda x: x,
) -> HereditaryStratigraphicAssemblage:
    """Deserialize a `HereditaryStratigraphicAssemblage` from a pandas
    DataFrame containing dstream surface data.

    Each row of the DataFrame represents a single hereditary stratigraphic
    surface, serialized as a hex string with associated dstream metadata.
    Surfaces are deserialized, converted to specimens, and assembled into
    a `HereditaryStratigraphicAssemblage`.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with dstream surface data.

        Required schema:
            - 'data_hex' : string
                Raw genome data as a hexadecimal string.
            - 'dstream_algo' : string or categorical
                Name of downstream curation algorithm
                (e.g., ``'dstream.steady_algo'``).
            - 'dstream_storage_bitoffset' : integer
                Bit offset of the dstream buffer field in ``data_hex``.
            - 'dstream_storage_bitwidth' : integer
                Bit width of the dstream buffer field in ``data_hex``.
            - 'dstream_T_bitoffset' : integer
                Bit offset of the dstream counter ("rank") field in
                ``data_hex``.
            - 'dstream_T_bitwidth' : integer
                Bit width of the dstream counter field in ``data_hex``.
            - 'dstream_S' : integer
                Capacity of the dstream buffer (number of differentia
                stored per annotation).
    progress_wrap : callable, optional
        Wrapper applied to the row iterator, e.g. ``tqdm.tqdm`` for a
        progress bar. Must accept and return an iterable. Default is the
        identity function (no wrapping).

    Returns
    -------
    HereditaryStratigraphicAssemblage
        Assemblage built from the deserialized surfaces.

    Raises
    ------
    ValueError
        If any required column is missing from the DataFrame.

    See Also
    --------
    surf_from_hex :
        Deserialize a single surface from a hex string.
    pop_to_assemblage :
        Create an assemblage from a collection of
        ``HereditaryStratigraphicColumn`` objects.
    assemblage_from_records :
        Deserialize an assemblage from a dict of builtin types.
    """
    missing = [c for c in _deserialization_columns if c not in df.columns]
    if missing:
        raise ValueError(
            "assemblage_from_dstream_df: missing required columns "
            f"{missing}",
        )

    def _iter_specimens():
        for _idx, row in progress_wrap(df.iterrows()):
            surface = surf_from_hex(
                hex_string=row["data_hex"],
                dstream_algo=eval(row["dstream_algo"], {"dstream": dstream}),
                dstream_S=row["dstream_S"],
                dstream_storage_bitoffset=row["dstream_storage_bitoffset"],
                dstream_storage_bitwidth=row["dstream_storage_bitwidth"],
                dstream_T_bitoffset=row["dstream_T_bitoffset"],
                dstream_T_bitwidth=row["dstream_T_bitwidth"],
            )
            yield _surf_to_specimen(surface)

    return HereditaryStratigraphicAssemblage(_iter_specimens())
