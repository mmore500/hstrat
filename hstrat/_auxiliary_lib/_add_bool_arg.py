import argparse


def add_bool_arg(
    parser: argparse.ArgumentParser,
    name: str,
    default: bool = False,
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
    """
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--" + name,
        dest=name.replace("-", "_"),
        action="store_true",
    )
    group.add_argument(
        "--no-" + name,
        dest=name.replace("-", "_"),
        action="store_false",
    )
    parser.set_defaults(**{name.replace("-", "_"): default})
