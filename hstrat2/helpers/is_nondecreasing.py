def is_nondecreasing(seq) -> bool:

    list_ = [*seq]
    return all(
        a <= b
        for a, b in zip(
            list_,
            list_[1:],
        )
    )
