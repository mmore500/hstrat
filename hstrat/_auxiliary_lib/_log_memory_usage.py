import logging
import subprocess
import typing


# adapted from https://stackoverflow.com/a/47411778/17332200
def log_memory_usage(logger: typing.Callable = logging.info) -> None:
    """Log memory use."""
    try:
        message = (
            "memory usage:\n"
            + subprocess.check_output(
                [
                    "free",
                    "--human",
                    "--total",
                ],
                shell=False,
            ).decode()
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        message = f"logging memory use failed: {e}"

    logger(message)
