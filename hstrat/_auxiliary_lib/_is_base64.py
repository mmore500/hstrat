import base64


# adapted from https://stackoverflow.com/a/45928164
def is_base64(data: str) -> bool:
    try:
        if isinstance(data, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            data_bytes = bytes(data, "ascii")
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(data_bytes)) == data_bytes
    except UnicodeEncodeError:
        return False
