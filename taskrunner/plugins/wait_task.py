import time
from ..core import BaseTaskRunner
from pydantic import BaseModel, Field


class WaitTaskConfig(BaseModel):
    seconds: int = Field(..., description="Number of seconds to wait", ge=0, le=3600)


class WaitTask(BaseTaskRunner):
    type_name = "wait"

    def run(self, config):
        # Validate config using Pydantic model
        validated_config = WaitTaskConfig(**config)
        print(f"[WaitTask] Waiting {validated_config.seconds} seconds...")
        time.sleep(validated_config.seconds)
        print("[WaitTask] Done.")
