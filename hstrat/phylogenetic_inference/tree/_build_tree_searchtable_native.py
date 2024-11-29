import logging
import warnings

while True:
    try:
        from ._build_tree_searchtable_cpp import (  # noqa: F401
            build_exploded,
            build_normal,
            RecordHolder_C,
        )

        break
    except ImportError:
        logging.info("native binaries not found, trying to compile them")

    try:
        import cppimport

        bts = cppimport.imp(
            "._build_tree_searchtable_cpp",
        )
        build_exploded = bts.build_exploded  # noqa: F401
        build_normal = bts.build_normal  # noqa: F401
        RecordHolder_C = bts.RecordHolder_C  # noqa: F401
        break
    except ImportError as e:
        warnings.warn(
            "native binaries not found and cppimport fallback failed. ",
        )
        raise e

    assert False
