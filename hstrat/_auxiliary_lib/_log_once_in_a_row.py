from functools import lru_cache
import logging


# Keep track of n different messages and then log again
# adapted from https://stackoverflow.com/a/66062313
@lru_cache(1)
def log_once_in_a_row(msg: str):
    logger = logging.getLogger("hstrat")
    logger.info(msg)
