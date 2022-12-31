def _to_tril(matrix):
    return [
        row[:row_idx] + [0.0] for row_idx, row in enumerate(matrix.tolist())
    ]
