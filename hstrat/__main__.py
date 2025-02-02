from ._auxiliary_lib import get_hstrat_version

if __name__ == "__main__":
    print(f"hstrat v{get_hstrat_version()}")
    print(
        """
Available commands (stabilized API):
$ python3 -m hstrat.dataframe.surface_build_tree
$ python3 -m hstrat.dataframe.surface_unpack_reconstruct
$ python3 -m hstrat.dataframe.surface_postprocess_trie

Available commands (experimental API):
$ python3 -m hstrat._auxiliary_lib._alifestd_as_newick_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_count_root_nodes
$ python3 -m hstrat._auxiliary_lib._alifestd_downsample_tips_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_join_roots
$ python3 -m hstrat._auxiliary_lib._alifestd_test_leaves_isomorphic_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_to_working_format
$ python3 -m hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col

For information on a command, invoke it with the --help flag.
""",
    )
