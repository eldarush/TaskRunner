"""
Log Task Plugin for TaskRunner.

This plugin provides a simple task that logs (prints) a message to the console.
It's useful for debugging, notifications, or simple output tasks.
"""

from ..core import BaseTaskRunner

class LogTask(BaseTaskRunner):
    """Task runner that prints a message to the console."""
    type_name = "log"

    def run(self, config):
        """Print a message to the console.
        
        Args:
            config (dict): Configuration dictionary containing:
                - message (str): The message to print
        """
        message = config.get("message", "")
        print(f"[LogTask] {message}")