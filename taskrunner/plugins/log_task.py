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
