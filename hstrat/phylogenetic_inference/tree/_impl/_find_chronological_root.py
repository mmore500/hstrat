import numbers
import typing

from iterpop import iterpop as ip
import networkx as nx

from ._find_chronological_roots import find_chronological_roots


def find_chronological_root(
    tree: nx.Graph,
    leaf_node_origin_times: typing.Dict[typing.Any, numbers.Number],
) -> str:
    """Convenience wrapper for `find_chronological_roots`, assuming phylogeny descends from a single common ancestor."""
    return ip.popsingleton(
        find_chronological_roots(tree, leaf_node_origin_times)
    )
