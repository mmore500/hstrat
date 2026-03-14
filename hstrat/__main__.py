from ._auxiliary_lib import begin_prod_logging, get_hstrat_version

if __name__ == "__main__":
    begin_prod_logging()
    print(f"hstrat v{get_hstrat_version()}")
    print(
        """
Available commands (stabilized API):
$ python3 -m hstrat.dataframe.surface_build_tree
$ python3 -m hstrat.dataframe.surface_postprocess_trie
$ python3 -m hstrat.dataframe.surface_unpack_reconstruct
$ python3 -m hstrat.dataframe.surface_validate_trie

For information on a command, invoke it with the --help flag.
""",
    )
