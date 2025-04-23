from ..genome_instrumentation import HereditaryStratigraphicSurface


def surf_to_hex(
    surface: HereditaryStratigraphicSurface,
    *,
    dstream_T_bitwidth: int = 32,
) -> str:
    """
    Serialize a HereditaryStratigraphicSurface object into a hex string
    representation.

    Serialized data comprises two components:
        1. dstream_T (the number of depositions elapsed) and
        2. dstream_storage (binary data of differentia values).

    The hex layout used is:

        0x...
            ########**************************************************
            ^                                                    ^
        dstream_T, length = `dstream_T_bitwidth` / 4            |
                                                                |
            dstream_storage, length = `item_bitwidth` / 4 * dstream_S

    This hex string can be reconstituted into a
    HereditaryStratigraphicSurface object by calling
    `HereditaryStratigraphicSurface.from_hex()` with the following
    parameters:
        - `dstream_T_bitoffset` = 0
        - `dstream_T_bitwidth` = `dstream_T_bitwidth`
        - `dstream_storage_bitoffset` = `dstream_T_bitwidth`
        - `dstream_storage_bitwidth` = `self.S * item_bitwidth`

    Parameters
    ----------
    item_bitwidth: int
        Number of storage bits used per differentia.
    dstream_T_bitwidth: int, default 32
        Number of bits used to store count of elapsed depositions.

    See Also
    --------
    surf_from_hex()
        Deserialize a surface from a hex string.
    """
    return surface._surface.to_hex(
        item_bitwidth=surface.GetStratumDifferentiaBitWidth(),
        T_bitwidth=dstream_T_bitwidth,
    )
