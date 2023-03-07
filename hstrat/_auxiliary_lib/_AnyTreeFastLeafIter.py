import typing

import anytree

from ._AnyTreeFastPreOrderIter import AnyTreeFastPreOrderIter


def AnyTreeFastLeafIter(
    node: anytree.AnyNode,
) -> typing.Iterator[anytree.AnyNode]:
    yield from filter(lambda x: x.is_leaf, AnyTreeFastPreOrderIter(node))
