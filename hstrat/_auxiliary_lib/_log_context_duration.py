import contextlib
import logging
import time
import typing


@contextlib.contextmanager
def log_context_duration(
    what: str,
    logger: callable = logging.info,
) -> typing.Iterable[None]:
    start = time.time()
    yield
    elapsed = time.time() - start
    logger(
        f"""exit log_seconds_elapsed for {what}
!!! {{"{what}": {elapsed}}}""",
    )
