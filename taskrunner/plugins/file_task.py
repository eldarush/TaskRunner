from ..core import BaseTaskRunner
from pydantic import BaseModel
from typing import Optional
import os


class FileTaskConfig(BaseModel):
    action: str = "create"  # "create" or "delete"
    path: str
    content: Optional[str] = ""


class FileTask(BaseTaskRunner):
    type_name = "file"

    def run(self, config):
        # Validate config using Pydantic model
        try:
            validated_config = FileTaskConfig(**config)
        except Exception as e:
            raise ValueError(f"Invalid config for file task: {e}")

        if validated_config.action == "create":
            print(f"[FileTask] Creating file {validated_config.path}")
            with open(validated_config.path, "w") as f:
                f.write(validated_config.content or "")
            print(f"[FileTask] File {validated_config.path} created successfully")
        elif validated_config.action == "delete":
            if os.path.exists(validated_config.path):
                print(f"[FileTask] Deleting file {validated_config.path}")
                os.remove(validated_config.path)
                print(f"[FileTask] File {validated_config.path} deleted successfully")
            else:
                print(f"[FileTask] File {validated_config.path} does not exist")
        else:
            raise ValueError(
                f"Unknown action '{validated_config.action}' for file task. Valid actions are 'create' and 'delete'")
