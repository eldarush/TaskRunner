"""
External Task Plugin for TaskRunner.

This is an example of an external plugin that can be discovered from an installed package.
"""

from taskrunner.core import BaseTaskRunner

class ExternalTask(BaseTaskRunner):
    """External task runner that demonstrates plugin discovery from installed packages."""
    type_name = "external"

    def run(self, config):
        """Print a message indicating this is an external plugin.
        
        Args:
            config (dict): Configuration dictionary containing:
                - message (str): The message to print
        """
        message = config.get("message", "This is an external plugin!")
        print(f"[ExternalTask] {message}")