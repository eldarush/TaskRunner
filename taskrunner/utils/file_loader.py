import json
import os
import yaml
from typing import List
from enum import Enum

from ..models.task_model import TaskModel


class FileLoaderMessages(Enum):
    FILE_NOT_FOUND = "Task file {} not found"
    UNSUPPORTED_FORMAT = "Unsupported file format. Use .json or .yaml"
    INVALID_TASKS_FORMAT = "Tasks file must contain a list of tasks."


class SupportedFormats(Enum):
    JSON = ".json"
    YAML = ".yaml"
    YML = ".yml"


def load_tasks_from_file(file_path: str) -> List[TaskModel]:
    """Load tasks from a JSON or YAML file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(FileLoaderMessages.FILE_NOT_FOUND.value.format(file_path))

    with open(file_path, "r") as f:
        if file_path.endswith(SupportedFormats.JSON.value):
            data = json.load(f)
        elif file_path.endswith((SupportedFormats.YAML.value, SupportedFormats.YML.value)):
            data = yaml.safe_load(f)
        else:
            raise ValueError(FileLoaderMessages.UNSUPPORTED_FORMAT.value)

    if not isinstance(data, list):
        raise ValueError(FileLoaderMessages.INVALID_TASKS_FORMAT.value)
    return [TaskModel(**t) for t in data]
