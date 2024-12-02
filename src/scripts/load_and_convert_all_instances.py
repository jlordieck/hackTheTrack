import argparse
from collections import defaultdict
from itertools import permutations
from pathlib import Path
from typing import NamedTuple
from zipfile import ZipFile

from tqdm import tqdm
from ugraph import EndNodeIdPair

from hackthetrack.dependencygraph import DependencyGraph, Link, LinkType
from hackthetrack.displib import DisplibInstance


def add_precedence_links(network: DependencyGraph) -> None:
    by_resource = defaultdict(list)
    for node in network.all_nodes:
        for resources in node.resources:
            by_resource[resources.name].append(node)

    links_to_add = []
    for group in by_resource.values():
        for origin, destination in permutations(group, r=2):
            cannot_collide = origin.train_id == destination.train_id
            if cannot_collide:
                continue
            links_to_add.append((EndNodeIdPair((origin.id, destination.id)), Link(LinkType.PRECEDENCE)))
    network.add_links(links_to_add)


def unzip_instances(path_to_instances: Path, path_to_dump: Path) -> None:
    path_to_dump.mkdir(exist_ok=True, parents=True)
    for set_of_instances in path_to_instances.glob("*.zip"):
        if set_of_instances.is_file():
            with ZipFile(set_of_instances, "r") as zip_ref:
                zip_ref.extractall(path_to_dump)


class Options(NamedTuple):
    path_to_instances: Path = Path("instances")
    path_to_save_instances: Path = Path("out/instances")
    path_to_dependency_graphs: Path = Path("out/dependency_graphs")
    path_to_figures: Path = Path("out/figures")
    do_standard_figure: bool = True
    do_precedence_figure: bool = False  # disabled as it takes a long time to compute


def load_and_convert_all_displib_instances(options: Options = Options()) -> None:
    unzip_instances(path_to_instances=options.path_to_instances, path_to_dump=options.path_to_save_instances)
    if options.do_precedence_figure or options.do_standard_figure:
        options.path_to_figures.mkdir(exist_ok=True, parents=True)
    options.path_to_dependency_graphs.mkdir(exist_ok=True, parents=True)

    all_paths = [
        path
        for directory in options.path_to_save_instances.iterdir()
        if directory.is_dir()
        for path in directory.glob("*.json")
    ]

    for path_to_instance in tqdm(all_paths, desc="Converting instances", colour="green", unit="instance"):
        network = DependencyGraph.from_displib_instance(DisplibInstance.from_json(path_to_instance))
        network.write_json(options.path_to_dependency_graphs / f"{path_to_instance.name}.DependencyGraph.json")
        if options.do_standard_figure:
            network.debug_plot(options.path_to_figures / f"{path_to_instance.stem}.jpg")
        if options.do_precedence_figure:
            add_precedence_links(network)
            network.debug_plot(options.path_to_figures / f"{path_to_instance.stem}.with_precedence_links.jpg")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_to_instances", type=Path, default=Path("instances"))
    parser.add_argument("--path_to_save_instances", type=Path, default=Path("out/instances"))
    parser.add_argument("--path_to_dependency_graphs", type=Path, default=Path("out/dependency_graphs"))
    parser.add_argument("--path_to_figures", type=Path, default=Path("out/figures"))
    parser.add_argument("--do_standard_figure", action="store_true")
    parser.add_argument("--do_precedence_figure", action="store_true")
    load_and_convert_all_displib_instances(Options(**vars(parser.parse_args())))
