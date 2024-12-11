from collections import Counter, defaultdict
from pathlib import Path

import plotly.graph_objects as go

from hackthetrack.dependencygraph.network import DependencyGraph
from hackthetrack.displib.load_displib_instance import DisplibInstance
from hackthetrack.statistics_logger import StatisticsLogger


def main():
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

        instance_id = path_to_instance.stem
        objectives_per_train = Counter(train_ids)
        logger.update_instance(instance_id, "objectives per train", dict(objectives_per_train))

        logger.update_instance(instance_id, "all trains have an objective", all_trains_have_objective)

        one_objective_per_train = len(train_ids) == len(set(train_ids))
        logger.update_instance(instance_id, "one objective per train", one_objective_per_train)

        objectives_on_last_node = all(objective_on_last_node.values())
        logger.update_instance(instance_id, "objective always on last node", objectives_on_last_node)

        lower_bounds_equal_thresholds = all([lb == threshold for lb, threshold in zip(lower_bounds, thresholds)])
        logger.update_instance(instance_id, "lb bounds == thresholds", lower_bounds_equal_thresholds)

        no_upper_bounds = all([ub is None for ub in upper_bounds])
        logger.update_instance(instance_id, "no ub bounds on any objective node", no_upper_bounds)

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

    plot = True
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
        logger.update_instance(instance_id, "objective type", objective_type)

        all_coeffs_are_one = all([coeff == 1.0 for coeff in coeffs if coeff != 0.0])
        logger.update_instance(instance_id, "all coeffs are 1", all_coeffs_are_one)

        if increments:
            logger.update_instance(instance_id, "occurrences of penalty values for steps", dict(increments))

        release_times = {resource.release_time for node in network.all_nodes for resource in node.resources}
        logger.update_instance(instance_id, "release times", sorted(release_times))

        objective_to_ignore = [
            threshold - lower < 0
            for threshold, lower, objective_type in zip(thresholds, lower_bounds, objective_types)
            if objective_type == "step"
        ]
        if len(objective_to_ignore) > 0:
            logger.update_instance(instance_id, "number of step objectives to ignore", sum(objective_to_ignore))

        if plot := True:
            # Create a plotly figure (no shit sherlock)
            figure = go.Figure()

            figure.add_trace(
                go.Scatter(
                    x=train_ids,
                    y=[None if ub is None else ub - lb for ub, lb in zip(upper_bounds, lower_bounds)],
                    mode="markers",
                    marker={"size": 10, "color": "blue"},
                    name="Upper bound relative to lb bound",
                )
            )

            figure.add_trace(
                go.Scatter(
                    x=train_ids,
                    y=[threshold - lower for threshold, lower in zip(thresholds, lower_bounds)],
                    mode="markers",
                    marker={"size": 10, "color": "red"},
                    name="Threshold relative to lb bound",
                )
            )

            figure.update_layout(
                title=f"Threshold and ub bound for {instance_id}",
                xaxis_title="Train ID",
                yaxis_title="Time",
                legend_title="Legend",
                template="plotly_white",
            )
            figure.write_html(Path(f"out/figures/{instance_id}_threshold_and_upper_bound.html"))


if __name__ == "__main__":
    main()
