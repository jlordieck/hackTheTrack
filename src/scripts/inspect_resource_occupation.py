from collections import defaultdict
from collections.abc import Collection
from typing import Hashable, NamedTuple

from _plotly_utils.colors import sample_colorscale
from plotly import express as px
from plotly import graph_objects as go
from ugraph.plot import ColorMap

from hackthetrack.dependencygraph import DependencyGraph


def create_colormap(elements: Collection[Hashable], default_color: str | None = None) -> ColorMap:
    count = len(elements)
    colors = sample_colorscale(px.colors.cyclical.Phase, samplepoints=[i / count for i in range(0, count)])
    if default_color is None:
        return ColorMap({key: color for key, color in zip(elements, colors)})
    cmap = defaultdict(lambda: default_color)
    cmap.update(zip(elements, colors))
    return ColorMap(cmap)


class Occupation(NamedTuple):
    start: float
    end: float
    resource: str
    train: int
    operation: int
    release_time: float
    min_duration: float
    start_lb: float
    start_ub: float


def find_all_occupations_with_dfs(network: DependencyGraph) -> tuple[Occupation, ...]:
    occupations = []
    for train in network.weak_components():
        train_nodes = train.all_nodes
        completed_time = [node.start_lb for node in train_nodes]
        start_time = [-float("inf") for _ in train_nodes]
        for node_index, parent_index in zip(*train.underlying_digraph.dfs(0)):
            if parent_index == -1:
                start_time[node_index] = 0
                start_lb = 0 if completed_time[node_index] is None else completed_time[node_index]
                completed_time[node_index] = start_lb + train_nodes[node_index].min_duration
                continue
            start_lb = completed_time[parent_index]
            start_time[node_index] = start_lb
            completed_time[node_index] = start_lb + train_nodes[node_index].min_duration
        for i, node in enumerate(train_nodes):
            for resource in node.resources:
                occupations.append(
                    Occupation(
                        start=start_time[i],
                        end=completed_time[i],
                        resource=resource.name,
                        train=node.train_id,
                        operation=node.index,
                        release_time=resource.release_time,
                        min_duration=node.min_duration,
                        start_lb=node.start_lb if node.start_lb is not None else 0,
                        start_ub=node.start_ub if node.start_ub is not None else float("inf"),
                    )
                )

    return tuple(occupations)


def _split_in_string_and_number(s: str) -> tuple[str, int]:
    i = 0
    for i, c in enumerate(s):
        if not c.isdigit():
            break
    i += 1
    return s[:i], int(s[i:])


def plot_occupations(occupations: Collection[Occupation]) -> go.Figure:
    # find all the resources, so we can sort them (assign an index)
    # resources have a string part (predecessor) and a number part (index)
    # sort on string and then on number
    resources = frozenset(occupation.resource for occupation in occupations)
    resource_to_index = {
        resource: i for i, resource in enumerate(sorted(resources, key=lambda x: _split_in_string_and_number(x)))
    }

    # find all the trains, so we can give them a color
    trains = sorted(frozenset(occupation.train for occupation in occupations))
    train_to_color = create_colormap(trains)

    figure = go.Figure()
    for occupation in occupations:
        figure.add_trace(
            go.Scatter(
                y=[occupation.start, occupation.end],
                x=[resource_to_index[occupation.resource], resource_to_index[occupation.resource]],
                mode="lines",
                line={"color": train_to_color[occupation.train], "width": 10},
                name=f"Train {occupation.train} Operation {occupation.operation}",
                hoverinfo="text",
                showlegend=False,
                hovertext=f"Resource: {occupation.resource}<br>Train: {occupation.train}<br>Operation: {occupation.operation}<br>Release time: {occupation.release_time}<br>Min duration: {occupation.min_duration}<br>Start LB: {occupation.start_lb}<br>Start UB: {occupation.start_ub}",
            )
        )
        # add lower bound with opacity 0.5
        figure.add_trace(
            go.Scatter(
                y=[occupation.end, occupation.end + occupation.release_time],
                x=[resource_to_index[occupation.resource], resource_to_index[occupation.resource]],
                mode="lines",
                line={"color": train_to_color[occupation.train], "width": 1, "dash": "dash"},
                name=f"Train {occupation.train} Operation {occupation.operation} Start LB",
                hoverinfo="text",
                showlegend=False,
            )
        )
    figure.update_layout(xaxis={"tickvals": list(range(len(resources))), "ticktext": list(resource_to_index.keys())})
    return figure
