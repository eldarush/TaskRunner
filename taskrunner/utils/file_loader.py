import json
import os
import yaml
from typing import List

from ..models.task_model import TaskModel


def load_tasks_from_file(file_path: str) -> List[TaskModel]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Task file {file_path} not found")

    with open(file_path, "r") as f:
        if file_path.endswith(".json"):
            data = json.load(f)
        elif file_path.endswith((".yaml", ".yml")):
            data = yaml.safe_load(f)
        else:
            raise ValueError("Unsupported file format. Use .json or .yaml")

    if not isinstance(data, list):
        raise ValueError("Tasks file must contain a list of tasks.")
    return [TaskModel(**t) for t in data]
