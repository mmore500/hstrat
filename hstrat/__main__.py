from ._auxiliary_lib import get_hstrat_version

if __name__ == "__main__":
    print(f"hstrat v{get_hstrat_version()}")
    print()
    print("Available commands:")
    print("$ python3 -m hstrat.dataframe.surface_unpack_reconstruct")
    print()
    print(
        "For information on a command, " "invoke it with the --help flag.",
    )
