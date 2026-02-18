import argparse


# adapted from https://stackoverflow.com/a/31347222
def add_bool_arg(
    parser: argparse.ArgumentParser,
    name: str,
    default: bool = False,
    help: str = "",
) -> None:
    """Add a ``--name/--no-name`` boolean flag pair to *parser*.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The argument parser to add the flag to.
    name : str
        The flag name (e.g., ``"insert"`` adds ``--insert``/``--no-insert``).
    default : bool, default False
        Default value when neither flag is provided.
    help : str, default ""
        Help text shown for the ``--name`` flag.
    """
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--" + name,
        dest=name.replace("-", "_"),
        action="store_true",
        help=help,
    )
    group.add_argument(
        "--no-" + name,
        dest=name.replace("-", "_"),
        action="store_false",
        help=f"disable --{name}",
    )
    parser.set_defaults(**{name.replace("-", "_"): default})
