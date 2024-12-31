from ._auxiliary_lib import get_hstrat_version

if __name__ == "__main__":
    print(f"hstrat v{get_hstrat_version()}")
    print()
    print("Available commands (stabilized API):")
    print("$ python3 -m hstrat.dataframe.surface_unpack_reconstruct")
    print()
    print("Available commands (experimental API):")
    print("$ python3 -m hstrat._auxiliary_lib._alifestd_as_newick_asexual")
    print()
    print(
        "For information on a command, " "invoke it with the --help flag.",
    )
