from pathlib import Path
from zipfile import ZipFile

from hackthetrack.dependencygraph import DependencyGraph
from hackthetrack.displib import DisplibInstance


def unzip_instances(path_to_instances: Path, path_to_dump: Path) -> None:
    path_to_dump.mkdir(exist_ok=True, parents=True)
    for set_of_instances in path_to_instances.glob("*.zip"):
        if set_of_instances.is_file():
            with ZipFile(set_of_instances, "r") as zip_ref:
                zip_ref.extractall(path_to_dump)


def load_and_convert_all_displib_instances() -> None:
    unzip_instances(path_to_instances=Path("instances"), path_to_dump=Path("out/instances"))
    figure_path = Path("out/figures")
    figure_path.mkdir(exist_ok=True, parents=True)
    dependency_graph_path = Path("out/dependency_graphs")
    dependency_graph_path.mkdir(exist_ok=True, parents=True)
    for folder_of_instances in Path("out/instances").glob("*"):
        if not folder_of_instances.is_dir():
            continue
        for path_to_instance in folder_of_instances.glob("*.json"):
            network = DependencyGraph.from_displib_instance(DisplibInstance.from_json(path_to_instance))
            network.debug_plot(figure_path / f"{path_to_instance.stem}.jpg")
            network.write_json(dependency_graph_path / f"{path_to_instance.stem}.DependencyGraph.json")


if __name__ == "__main__":
    load_and_convert_all_displib_instances()
