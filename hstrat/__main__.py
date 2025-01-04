from ._auxiliary_lib import get_hstrat_version

if __name__ == "__main__":
    print(f"hstrat v{get_hstrat_version()}")
    print()
    print("Available commands (stabilized API):")
    print("$ python3 -m hstrat.dataframe.surface_build_tree")
    print("$ python3 -m hstrat.dataframe.surface_unpack_reconstruct")
    print("$ python3 -m hstrat.dataframe.surface_postprocess_trie")
    print()
    print("Available commands (experimental API):")
    print("$ python3 -m hstrat._auxiliary_lib._alifestd_as_newick_asexual")
    print(
        "$ python3 -m hstrat._auxiliary_lib._alifestd_downsample_tips_asexual"
    )
    print(
        "$ python3 -m hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col"
    )
    print()
    print(
        "For information on a command, " "invoke it with the --help flag.",
    )
