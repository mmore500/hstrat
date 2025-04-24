import types
import typing

from downstream import dsurf

from ..genome_instrumentation import HereditaryStratigraphicSurface


def surf_from_hex(
    hex_string: str,
    dstream_algo: types.ModuleType,
    *,
    dstream_S: int,
    dstream_storage_bitoffset: typing.Optional[int] = None,
    dstream_storage_bitwidth: int,
    dstream_T_bitoffset: int = 0,
    dstream_T_bitwidth: int = 32,
) -> HereditaryStratigraphicSurface:
    """
    Deserialize a HereditaryStratigraphicSurface object from a hex string
    representation.

    Hex string representation needs exactly two contiguous parts:
    1. dstream_T (which is the number of depositions elapsed), and
    2. dstream_storage (which holds all the stored differentiae).

    Data in hex string representation should use big-endian byte order.

    Parameters
    ----------
    hex_string: str
        Hex string to be parsed, which can be uppercase or lowercase.
    dstream_algo: module
        Dstream algorithm for curation of retained differentia.
    dstream_storage_bitoffset: int, default dstream_T_bitwidth
        Number of bits before the storage.
    dstream_storage_bitwidth: int
        Number of bits used for storage.
    dstream_T_bitoffset: int, default 0
        Number of bits before dstream_T.
    dstream_T_bitwidth: int, default 32
        Number of bits used to store dstream_T.
    dstream_S: int
        Number of buffer sites available to store differentiae.

        Determines how many differentiae are unpacked from storage.

    See Also
    --------
    surf_to_hex()
        Serialize a surface into a hex string.
    """
    if dstream_storage_bitoffset is None:
        dstream_storage_bitoffset = dstream_T_bitwidth
    assert dstream_storage_bitwidth % dstream_S == 0
    return HereditaryStratigraphicSurface(
        dsurf.Surface.from_hex(
            hex_string,
            dstream_algo,
            S=dstream_S,
            storage_bitoffset=dstream_storage_bitoffset,
            storage_bitwidth=dstream_storage_bitwidth,
            T_bitoffset=dstream_T_bitoffset,
            T_bitwidth=dstream_T_bitwidth,
        ),
        stratum_differentia_bit_width=dstream_storage_bitwidth // dstream_S,
    )
