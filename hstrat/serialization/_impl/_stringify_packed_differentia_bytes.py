from base64 import b64encode

import typing_extensions


def stringify_packed_differentia_bytes(
    buffer: typing_extensions.Buffer,
) -> str:
    """Convert packed differentia bytes to a string representation."""
    encoded_bytes = b64encode(buffer)
    encoded_str = encoded_bytes.decode()
    return encoded_str
