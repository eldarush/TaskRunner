from ..core import BaseTaskRunner
from pydantic import BaseModel, Field
from typing import Optional
import os
from enum import Enum


class FileAction(str, Enum):
    CREATE = "create"
    DELETE = "delete"


class FileTaskConfig(BaseModel):
    action: FileAction = Field(..., description="Action to perform on the file")
    path: str = Field(..., description="Path to the file", min_length=1)
    content: Optional[str] = Field("", description="Content to write when creating a file")


class FileTask(BaseTaskRunner):
    type_name = "file"

    def run(self, config):
        # Validate config using Pydantic model
        validated_config = FileTaskConfig(**config)

        if validated_config.action == FileAction.CREATE:
            print(f"[FileTask] Creating file {validated_config.path}")
            with open(validated_config.path, "w") as f:
                f.write(validated_config.content or "")
            print(f"[FileTask] File {validated_config.path} created successfully")
        elif validated_config.action == FileAction.DELETE:
            if os.path.exists(validated_config.path):
                print(f"[FileTask] Deleting file {validated_config.path}")
                os.remove(validated_config.path)
                print(f"[FileTask] File {validated_config.path} deleted successfully")
            else:
                print(f"[FileTask] File {validated_config.path} does not exist")
        else:
            raise ValueError(
                f"Unknown action '{validated_config.action}' for file task. Valid actions are '{str(FileAction.CREATE)}' and '{str(FileAction.DELETE)}'")
