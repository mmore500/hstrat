from joinem import dataframe_cli

from .._auxiliary_lib import get_hstrat_version
from ._surface_unpack_reconstrct import surface_unpack_reconstruct

if __name__ == "__main__":
    dataframe_cli(
        description="Unpack dstream buffer and counter from genome data  serialized into a single hexadecimal data field, TODO.",
        module="hstrat.dataframe.surface_unpack_reconstruct",
        version=get_hstrat_version(),
        output_dataframe_op=surface_unpack_reconstruct,
    )
