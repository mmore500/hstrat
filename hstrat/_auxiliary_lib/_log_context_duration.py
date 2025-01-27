import contextlib
import json
import logging
import time
import typing


@contextlib.contextmanager
def log_context_duration(
    what: str,
    logger: callable = logging.info,
) -> typing.Iterable[None]:
    logger(f"enter log_context_duration for {what}")
    start = time.time()
    yield
    elapsed = time.time() - start
    logger(
        f"""exit log_context_duration for {what}
!!! {{{json.dumps(what)}: {elapsed}}}""",
    )
