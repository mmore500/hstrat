import logging

from joinem import dataframe_cli

from .._auxiliary_lib import get_hstrat_version
from ._surface_unpack_reconstrct import surface_unpack_reconstruct

if __name__ == "__main__":
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
    )
    dataframe_cli(
        description="Unpack dstream buffer and counter from genome data  serialized into a single hexadecimal data field, TODO.",
        module="hstrat.dataframe.surface_unpack_reconstruct",
        version=get_hstrat_version(),
        output_dataframe_op=surface_unpack_reconstruct,
    )
