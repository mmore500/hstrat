import logging
import warnings

while True:
    try:
        from ._build_tree_searchtable_cpp import (  # noqa: F401
            RecordHolder_C,
            build_exploded,
            build_normal,
        )

        break
    except ImportError:
        logging.info("native binaries not found, trying to compile them")

    try:
        import cppimport.import_hook  # noqa: F401

        from ._build_tree_searchtable_cpp import (  # noqa: F401
            RecordHolder_C,
            build_exploded,
            build_normal,
        )

        break
    except ImportError as e:
        warnings.warn(
            "native binaries not found and cppimport fallback failed. ",
        )
        raise e

    assert False
