import time
from ..core import BaseTaskRunner


class WaitTask(BaseTaskRunner):
    type_name = "wait"

    def run(self, config):
        seconds = config.get("seconds", 1)
        print(f"[WaitTask] Waiting {seconds} seconds...")
        time.sleep(seconds)
        print("[WaitTask] Done.")
