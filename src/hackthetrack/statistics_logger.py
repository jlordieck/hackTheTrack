from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

LOGGING_PATH = Path("out/statistics")


@dataclass(frozen=True, slots=True)
class StatisticsLogger:
    base_path: Path = LOGGING_PATH

    def __post_init__(self):
        self.base_path.mkdir(exist_ok=True, parents=True)

    def _get_instance_file(self, instance_name: str) -> Path:
        return self.base_path / f"{instance_name}.yaml"

    def update_instance(self, instance_name: str, key: str, value: Any) -> None:
        """
        Update or add information for a specific key in the instance's YAML file.

        If the file or the key does not exist, it is created.
        """
        data = self.load_instance_data(instance_name)
        data[key] = value

        with open(self._get_instance_file(instance_name), "w") as f:
            yaml.dump(data, f)

    def load_instance_data(self, instance_name: str) -> dict:
        """
        Retrieve all data for a given instance.
        Returns an empty dictionary if the file does not exist.
        """
        file_path = self._get_instance_file(instance_name)
        if file_path.exists():
            with open(file_path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def delete_key(self, instance_name: str, key: str):
        """
        Delete a key from the instance's YAML file.
        If the key does not exist, nothing happens.
        """
        data = self.load_instance_data(instance_name)
        if key in data:
            del data[key]
            with open(self._get_instance_file(instance_name), "w") as f:
                yaml.dump(data, f)

    def delete_key_on_all_instances(self, key: str):
        """
        Delete a key from all instances.
        If the key does not exist in any instance, nothing happens.
        """
        for instance_file in self.base_path.glob("*.yaml"):
            self.delete_key(instance_file.stem, key)


if __name__ == "__main__":
    logger = StatisticsLogger()
    logger.delete_key_on_all_instances("no upper bounds on any objective node")
