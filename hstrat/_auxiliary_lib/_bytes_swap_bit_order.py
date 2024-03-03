import numpy as np
import typing_extensions


def bytes_swap_bit_order(buffer: typing_extensions.Buffer) -> bytes:
    r"""Reverse the bit order of each byte in a given buffer.

    Parameters
    ----------
    buffer : typing_extensions.Buffer
        Input buffer whose bits in each byte are to be reversed.

    Returns
    -------
    bytes
        A new buffer with the bit order of each byte in the input buffer
        reversed.

    Examples
    --------
    >>> input_bytes = b'\x01\x02'
    >>> bytes_swap_bit_order(input_bytes)
    b'\x80\x40'
    """
    numpy_bytes = np.frombuffer(buffer, dtype=np.uint8)
    numpy_bits = np.unpackbits(numpy_bytes, bitorder="little")
    return np.packbits(numpy_bits, bitorder="big").tobytes()
