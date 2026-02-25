import logging

from ._configure_prod_logging import configure_prod_logging
from ._get_hstrat_version import get_hstrat_version


def begin_prod_logging() -> None:
    configure_prod_logging()
    logging.info(f"hstrat version {get_hstrat_version()}")
