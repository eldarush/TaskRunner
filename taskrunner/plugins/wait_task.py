"""
Wait Task Plugin for TaskRunner.

This plugin provides a task that pauses execution for a specified number of seconds.
It's useful for adding delays between tasks or simulating processing time.
"""

import time
from ..core import BaseTaskRunner

class WaitTask(BaseTaskRunner):
    """Task runner that pauses execution for a specified number of seconds."""
    type_name = "wait"

    def run(self, config):
        """Pause execution for a specified number of seconds.
        
        Args:
            config (dict): Configuration dictionary containing:
                - seconds (int): Number of seconds to wait (default: 1)
        """
        seconds = config.get("seconds", 1)
        print(f"[WaitTask] Waiting {seconds} seconds...")
        time.sleep(seconds)
        print("[WaitTask] Done.")