from ..core import BaseTaskRunner
from pydantic import BaseModel, Field


class LogTaskConfig(BaseModel):
    message: str = Field(..., description="The message to log")


class LogTask(BaseTaskRunner):
    type_name = "log"

    def run(self, config):
        # Validate config using Pydantic model
        validated_config = LogTaskConfig(**config)
        print(f"[LogTask] {validated_config.message}")