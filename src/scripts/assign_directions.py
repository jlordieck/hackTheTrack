from dataclasses import replace
from itertools import chain
from typing import Literal, NamedTuple

from ugraph import EndNodeIdPair, NodeId, NodeIndex, ThreeDCoordinates

from hackthetrack.dependencygraph import DependencyGraph, Link, LinkType, Node, NodeType


class LayoutOptions(NamedTuple):
    layout_algorithm: Literal["fr"] = "fr"


def use_igraph_to_update_x_and_y_coordinates(
    network: DependencyGraph, options: LayoutOptions = LayoutOptions()
) -> None:
    copied = network.shallow_copy
    resources = frozenset(
        resource.name for resource in chain.from_iterable(node.resources for node in network.all_nodes)
    )
    zero_coordinates = ThreeDCoordinates(x=0, y=0, z=0)
    base_node = Node(
        NodeId(f"resource_{0}"),
        index=-1,
        train_id=-1,
        start_lb=None,
        start_ub=None,
        min_duration=0,
        resources=[],
        successors=[],
        coordinates=zero_coordinates,
        node_type=NodeType.RESOURCE,
    )
    copied.add_nodes([replace(base_node, id=NodeId(f"resource_{resource}")) for resource in resources])
    links_to_add = []
    for node in copied.all_nodes:
        for resource in node.resources:
            links_to_add.append(
                (EndNodeIdPair((node.id, NodeId(f"resource_{resource.name}"))), Link(link_type=LinkType.PRECEDENCE))
            )
    copied.add_links(links_to_add)

    layout = copied.underlying_digraph.layout(options.layout_algorithm, dim=2, weights=None, niter=10000)
    resource_coordinates = {
        resource_name: ThreeDCoordinates(x=layout[i][0], y=layout[i][1], z=0)
        for i, resource_name in enumerate(resources, start=network.n_count)
    }

    nan_coordinates = ThreeDCoordinates(x=float("nan"), y=float("nan"), z=float("nan"))
    for i, node in enumerate(network.all_nodes):
        i: NodeIndex
        resource_locations = tuple(resource_coordinates[resource.name] for resource in node.resources)
        if len(resource_locations) > 0:
            average_coordinates = ThreeDCoordinates.create_mean_location_coordinates(resource_locations)
        else:
            average_coordinates = nan_coordinates
        network.replace_node(i, replace(node, coordinates=average_coordinates))
