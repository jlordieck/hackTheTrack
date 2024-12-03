from pathlib import Path

import plotly.graph_objects as go

from hackthetrack.dependencygraph.network import DependencyGraph
from hackthetrack.displib.load_displib_instance import DisplibInstance

displib_directory = Path("out/instances/displib_instances_phase1")

for path_to_instance in displib_directory.glob("*.json"):
    instance = DisplibInstance.from_json(path_to_instance)
    network = DependencyGraph.from_displib_instance(instance)

    objectives = instance.objectives
    thresholds = []
    lower_bounds = []
    upper_bounds = []
    train_ids = []

    for objective in objectives:
        train_id = objective["train"]
        train_ids.append(train_id)
        operation = objective["operation"]
        node = network.node_by_train_id_and_index(train_id, operation)
        thresholds.append(objective["threshold"])
        if node.start_lb is None:
            lower_bounds.append(0.0)
        else:
            lower_bounds.append(node.start_lb)
        if node.start_ub is None:
            upper_bounds.append(objective["threshold"])
        else:
            upper_bounds.append(node.start_ub)

    print(f"Instance {path_to_instance.stem}")
    if len(train_ids) == len(set(train_ids)):
        print(f"at most one objective for every train.")
    else:
        print(f"multiple objectives for at least one train.")

    if all([lb == threshold for lb, threshold in zip(lower_bounds, thresholds)]):
        print(f"lower bounds and thresholds are equivalent.")
    else:
        print(f"lower bounds and thresholds differ.")
    print()

    plot = True
    if plot:
        # Create a plotly figure
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=train_ids,
                y=[upper - lower for upper, lower in zip(upper_bounds, lower_bounds)],
                mode="markers",
                marker=dict(size=10, color="blue"),
                name="Upper bound relative to lower bound",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=train_ids,
                y=[threshold - lower for threshold, lower in zip(thresholds, lower_bounds)],
                mode="markers",
                marker=dict(size=10, color="red"),
                name="Threshold relative to lower bound",
            )
        )

        # Update layout for better readability
        fig.update_layout(
            title=f"Threshold and upper bound for {path_to_instance.stem}",
            xaxis_title="Train ID",
            yaxis_title="Time",
            legend_title="Legend",
            template="plotly_white",
        )

        # Display the figure
        fig.show()
