"""
File Task Plugin for TaskRunner.

This plugin provides tasks for file operations such as creating and deleting files.
It's useful for setting up test environments, cleaning up temporary files, or
managing file-based resources.
"""

from ..core import BaseTaskRunner
from pydantic import BaseModel
from typing import Optional
import os

class FileTaskConfig(BaseModel):
    """Configuration model for file tasks."""
    action: str = "create"  # "create" or "delete"
    path: str
    content: Optional[str] = ""

class FileTask(BaseTaskRunner):
    """Task runner for file operations (create/delete)."""
    type_name = "file"

    def run(self, config):
        """Perform file operations based on the configuration.
        
        Args:
            config (dict): Configuration dictionary containing:
                - action (str): The action to perform ("create" or "delete")
                - path (str): The file path to operate on
                - content (str, optional): Content to write when creating a file
                
        Raises:
            ValueError: If the configuration is invalid or the action is unknown
        """
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
            raise ValueError(f"Unknown action '{validated_config.action}' for file task. Valid actions are 'create' and 'delete'")