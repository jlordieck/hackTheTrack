from pathlib import Path

import plotly.graph_objects as go

from hackthetrack.dependencygraph.network import DependencyGraph
from hackthetrack.displib.load_displib_instance import DisplibInstance

displib_directory = Path("out/instances/displib_instances_phase1")

for path_to_instance in filter(lambda x: x.stem == "line2_headway_0", displib_directory.glob("*.json")):
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
        lower_bounds.append(node.start_lb)
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

        # Add lower and upper bound as filled area
        fig.add_trace(
            go.Scatter(
                x=train_ids, y=lower_bounds, mode="lines", line=dict(width=0), showlegend=False, name="Lower Bound"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=train_ids,
                y=upper_bounds,
                fill="tonexty",  # Fill area between the lines
                mode="lines",
                line=dict(width=0),
                fillcolor="rgba(0, 100, 200, 0.2)",
                name="Bound Range",
            )
        )

        # Add threshold points
        fig.add_trace(
            go.Scatter(x=train_ids, y=thresholds, mode="markers", marker=dict(size=10, color="red"), name="Thresholds")
        )

        # Update layout for better readability
        fig.update_layout(
            title=f"Objectives and Node Bounds for {path_to_instance.stem}",
            xaxis_title="Train ID",
            yaxis_title="Time",
            legend_title="Legend",
            template="plotly_white",
        )

        # Display the figure
        fig.show()
