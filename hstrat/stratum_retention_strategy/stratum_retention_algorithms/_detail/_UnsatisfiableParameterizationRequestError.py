class UnsatisfiableParameterizationRequestError(ValueError):
    """Raised when parameter with required properties cannot be found.

    May be due to inexistance of satisfactory parameter or due to violation of
    assumed monotonic relationship between parameter and focal property.
    """
