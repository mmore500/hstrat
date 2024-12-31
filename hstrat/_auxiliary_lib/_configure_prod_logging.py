import logging
import os
import sys


def configure_prod_logging() -> None:
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
    )
    if not sys.__stdout__.isatty():
        os.environ["TQDM_MININTERVAL"] = "5"
