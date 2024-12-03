from collections import defaultdict
from pathlib import Path

import plotly.graph_objects as go

from hackthetrack.dependencygraph.network import DependencyGraph
from hackthetrack.displib.load_displib_instance import DisplibInstance
from hackthetrack.statistics_logger import StatisticsLogger

logger = StatisticsLogger()
displib_directory = Path("out/instances/displib_instances_phase1")

for path_to_instance in filter(lambda x: True, displib_directory.glob("*.json")):
    instance = DisplibInstance.from_json(path_to_instance)
    network = DependencyGraph.from_displib_instance(instance)

    objectives = instance.objectives
    thresholds, lower_bounds, upper_bounds, train_ids, objective_types, coeffs = [], [], [], [], [], []
    increments = defaultdict(int)
    objective_on_last_node = dict()

    all_train_ids = [train["id"] for train in instance.trains]
    for train_id in all_train_ids:
        objective_on_last_node[train_id] = False

    for objective in objectives:
        train_id = objective["train"]
        train_ids.append(train_id)
        operation = objective["operation"]
        node = network.node_by_train_id_and_index(train_id, operation)
        last_index = instance.trains[train_id]["operations"][-1].index

        if node.index == last_index:
            objective_on_last_node[train_id] = True

        thresholds.append(objective["threshold"])
        lower_bounds.append(node.start_lb if node.start_lb is not None else 0.0)
        upper_bounds.append(node.start_ub)

        assert objective["coeff"] or objective["increment"]
        if objective["coeff"] and objective["increment"]:
            objective_types.append("mixed")
        else:
            objective_types.append("linear" if objective["coeff"] != 0.0 else "step")

        coeffs.append(objective["coeff"])
        if objective["increment"] != 0:
            increments[objective["increment"]] += 1

    all_trains_have_objective = len(set(train_ids)) == len(all_train_ids)
    logger.update_instance(path_to_instance.stem, "all trains have an objective", all_trains_have_objective)

    one_objective_per_train = len(train_ids) == len(set(train_ids))
    logger.update_instance(path_to_instance.stem, "one objective per train", one_objective_per_train)

    objectives_on_last_node = all(objective_on_last_node.values())
    logger.update_instance(path_to_instance.stem, "objective always on last node", objectives_on_last_node)

    lower_bounds_equal_thresholds = all([lb == threshold for lb, threshold in zip(lower_bounds, thresholds)])
    logger.update_instance(path_to_instance.stem, "lower bounds == thresholds", lower_bounds_equal_thresholds)

    no_upper_bounds = all([ub == None for ub in upper_bounds])
    logger.update_instance(path_to_instance.stem, "no upper bounds on any objective node", no_upper_bounds)

    objective_type = "linear" if all([objective_type == "linear" for objective_type in objective_types]) else "mixed"
    if objective_type == "mixed":
        objective_type = "step" if all([objective_type == "step" for objective_type in objective_types]) else "mixed"
    logger.update_instance(path_to_instance.stem, "objective type", objective_type)

    all_coeffs_are_one = all([coeff == 1.0 for coeff in coeffs if coeff != 0.0])
    logger.update_instance(path_to_instance.stem, "all coeffs are 1", all_coeffs_are_one)

    if increments:
        logger.update_instance(path_to_instance.stem, "occurrences of penalty values for steps", dict(increments))

    objective_to_ignore = [
        threshold - lower < 0
        for threshold, lower, objective_type in zip(thresholds, lower_bounds, objective_types)
        if objective_type == "step"
    ]
    if objective_to_ignore:
        logger.update_instance(path_to_instance.stem, "number of step objectives to ignore", sum(objective_to_ignore))

    plot = False
    if plot:
        # Create a plotly figure
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=train_ids,
                y=[upper - lower if upper is not None else None for upper, lower in zip(upper_bounds, lower_bounds)],
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
