# adapted from https://stackoverflow.com/a/11443871/17332200
def div_range(start: int, end: int, divide_by: int):

    assert divide_by > 0
    assert start >= 0
    assert end >= 0

    while start > end:
        yield start
        start //= divide_by
