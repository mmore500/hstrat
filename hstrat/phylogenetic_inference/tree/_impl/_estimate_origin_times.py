import numbers
import typing

import networkx as nx
import numpy as np
import sortedcontainers as sc


def estimate_origin_times(
    graph: nx.Graph,
    leaf_node_origin_times: typing.Dict[typing.Any, numbers.Number],
) -> typing.Dict[str, numbers.Number]:
    """Estimate origin time of graph nodes by working backward from
    phylogenetic depths of leaf nodes using "length" attributes on graph
    edges.

    Keys in `leaf_node_origin_times` should correspond to nodes in graph.
    """

    assert all(data["length"] >= 0 for _a, _b, data in graph.edges(data=True))

    # ensure clean slate for origin time setup
    for _node, data in graph.nodes(data=True):
        if "origin_time" in data:
            del data["origin_time"]

    # setup origin times of leaf nodes in graph
    leaf_nodes = leaf_node_origin_times.keys()
    for leaf_node in leaf_nodes:
        graph.nodes[leaf_node]["origin_time"] = leaf_node_origin_times[
            leaf_node
        ]

    # starting from leaf nodes...
    visited_nodes = set()  # fully explored nodes
    discovered_nodes = sc.SortedSet(
        leaf_nodes,
        key=lambda node: graph.nodes[node]["origin_time"],
    )  # nodes eligible to visit next, sorted chronologically (deepest last)

    # ... traverse graph: discover nodes and calculate their origin times
    # in reverse chronological order
    while len(visited_nodes) < len(graph):
        # pop oldest discovered node, mark visited, discover its neighbors
        cur_node = discovered_nodes.pop(-1)
        visited_nodes.add(cur_node)

        newly_discovered_nodes = set(graph.neighbors(cur_node)) - (
            visited_nodes | discovered_nodes
        )
        # enforce chronological consistency:
        # ensure that nodes are only visited after all children have been
        # visited and at most one unvisited neighbor (ancestor) remains
        newly_discovered_nodes -= {
            node
            for node in newly_discovered_nodes
            if sum(
                "origin_time" not in graph.nodes[neighbor]
                for neighbor in graph.neighbors(node)
            )
            > 1
        }
        # give newly discovered nodes origin time estimates
        for newly_discovered_node in newly_discovered_nodes:
            assert "origin_time" not in graph[newly_discovered_node]
            # estimate origin_time of cur node
            descendant_origin_times = [
                graph.nodes[neighbor_node]["origin_time"]
                for neighbor_node in graph.neighbors(newly_discovered_node)
                if "origin_time" in graph.nodes[neighbor_node]
            ]
            estimated_origin_times = [
                graph.nodes[neighbor_node]["origin_time"]
                - graph[newly_discovered_node][neighbor_node]["length"]
                for neighbor_node in graph.neighbors(newly_discovered_node)
                if "origin_time" in graph.nodes[neighbor_node]
            ]
            assert estimated_origin_times
            origin_time = min(
                np.mean(estimated_origin_times),
                min(descendant_origin_times),
            )
            graph.nodes[newly_discovered_node]["origin_time"] = origin_time

        # register newly discovered nodes as eligible to visit next
        discovered_nodes.update(newly_discovered_nodes)

    return {node: graph.nodes[node]["origin_time"] for node in graph.nodes}
