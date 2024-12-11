from pathlib import Path
import hexaly.optimizer

from hackthetrack.dependencygraph.network import DependencyGraph
from hackthetrack.displib.load_displib_instance import DisplibInstance


def main():
    displib_instance_path = Path("out/instances/displib_instances_phase1/line1_critical_0.json")
    instance = DisplibInstance.from_json(displib_instance_path)

    network = DependencyGraph.from_displib_instance(instance)
    objective_nodes = [
        network.node_by_train_id_and_index(obj["train"], obj["operation"]) for obj in instance.objectives
    ]
    objective_node_indices = [node.index for node in objective_nodes]

    num_operations = len(network.all_nodes)

    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        model = optimizer.get_model()

        operations = [model.interval(node.start_lb if node.start_lb else 0, horizon) for node in network.all_nodes]
        operation_array = model.array(operations)

        resource_allocation = model.array([model.list(num_operations) for _ in range(num_resources)])

        operation_to_train_array = model.array(operation_to_train)

        # lower bound on operation duration and upper bound on start time if applicable
        for i, operation in enumerate(operations):
            model.add_constraint(model.length(operation) >= network.all_nodes[i].min_duration)
            if network.all_nodes[i].start_ub is not None:
                model.add_constraint(model.start(operation) <= network.all_nodes[i].start_ub)

        # ordering of operations on the same resource with release times if subsequent operations are on different trains
        for r in range(num_resources):
            sequence = resource_allocation[r]
            release_times_for_resource = model.array(release_times[r])
            sequence_lambda = model.lambda_function(
                lambda i: operation_array[sequence[i]]
                + (operation_to_train_array[sequence[i]] != operation_to_train_array[sequence[i + 1]])
                * release_times_for_resource[sequence[i]]
                < operation_array[sequence[i + 1]]
            )
            model.constraint(model.and_(model.range(0, model.count(sequence) - 1), sequence_lambda))

        # no-wait and routing of trains
        for node in network.all_nodes:
            neighbors = network.neighbors(node.id, "out")
            if len(neighbors) == 0:
                continue
            elif len(neighbors) == 1:
                model.add_constraint(
                    model.end(operation_array[node.index]) == model.start(operation_array[neighbors[0].index])
                )
            else:
                model.add_constraint(
                    model.or_(
                        [
                            model.end(operation_array[node.index]) == model.start(operation_array[neighbor.index])
                            for neighbor in neighbors
                        ]
                    )
                )

        # activate all trains

        # objective
        model.minimize(model.sum(model.start(operation_array[i]) for i in objective_node_indices))
        model.close()

        optimizer.solve()


if __name__ == "__main__":
    main()
