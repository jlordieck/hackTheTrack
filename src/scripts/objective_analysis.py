from pathlib import Path

import plotly.graph_objects as go

from hackthetrack.dependencygraph.network import DependencyGraph
from hackthetrack.displib.load_displib_instance import DisplibInstance
from hackthetrack.statistics_logger import StatisticsLogger

logger = StatisticsLogger()
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
        upper_bounds.append(node.start_ub)

    if len(train_ids) == len(set(train_ids)):
        logger.update_instance(path_to_instance.stem, "one objective per train", True)
    else:
        logger.update_instance(path_to_instance.stem, "one objective per train", False)

    if all([lb == threshold for lb, threshold in zip(lower_bounds, thresholds)]):
        logger.update_instance(path_to_instance.stem, "lower bounds == thresholds", True)
    else:
        logger.update_instance(path_to_instance.stem, "lower bounds == thresholds", False)

    if all([ub == None for ub in upper_bounds]):
        logger.update_instance(path_to_instance.stem, "no upper bounds on any objective node", True)
    else:
        logger.update_instance(path_to_instance.stem, "no upper bounds on any objective node", False)

    plot = False
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
