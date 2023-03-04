import numbers
import typing

import networkx as nx

from ._estimate_origin_times import estimate_origin_times


def find_chronological_roots(
    graph: nx.Graph,
    leaf_node_origin_times: typing.Dict[typing.Any, numbers.Number],
) -> typing.List[str]:
    """Work backward from known phylogenetic depths of leaf nodes to identify
    a likely most ancient ancestor.

    Keys in `leaf_node_origin_times` should correspond to nodes in graph.
    """

    node_origin_times = estimate_origin_times(graph, leaf_node_origin_times)

    # extract root node of each connected component
    root_nodes = [
        min(component, key=lambda node: node_origin_times[node])
        for component in nx.connected_components(graph)
    ]

    return [graph.nodes[root_node]["taxon_label"] for root_node in root_nodes]
