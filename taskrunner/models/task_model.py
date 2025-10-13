from pydantic import BaseModel, Field
from typing import Dict


class TaskModel(BaseModel):
    name: str = Field(..., description="The name of the task")
    type: str = Field(..., description="The type of the task")
    config: Dict = Field(default_factory=dict, description="The configuration of the task")
