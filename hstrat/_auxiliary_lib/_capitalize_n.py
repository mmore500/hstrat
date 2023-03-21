def capitalize_n(string: str, n: int) -> str:
    """Create a copy of `string` with the first `n` characers capitalized.

    If `n` is negative, the last `n` characters will be capitalized.

    Examples
    --------
    >>> capitalize_n('hello world', 2)
    'HEllo world'
    >>> capitalize_n('goodbye', 4)
    'GOODbye'
    """
    return (
        string[:n].upper() + string[n:]
        if n >= 0
        else string[:n] + string[n:].upper()
    )
