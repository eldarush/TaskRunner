"""
Task model for TaskRunner.

This module defines the data model for tasks.
"""

from pydantic import BaseModel, Field
from typing import Dict

class TaskModel(BaseModel):
    """Pydantic model for task definitions."""
    name: str = Field(..., description="The name of the task")
    type: str = Field(..., description="The type of the task")
    config: Dict = Field(default_factory=dict, description="The configuration of the task")