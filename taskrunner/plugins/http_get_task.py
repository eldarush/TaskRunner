"""
HTTP GET Task Plugin for TaskRunner.

This plugin provides a task that makes an HTTP GET request to a specified URL
and prints the status code. It's useful for checking the availability of web
services or APIs.
"""

import requests
from ..core import BaseTaskRunner

class HttpGetTask(BaseTaskRunner):
    """Task runner that makes an HTTP GET request to a URL."""
    type_name = "http_get"

    def run(self, config):
        """Make an HTTP GET request to a URL and print the status code.
        
        Args:
            config (dict): Configuration dictionary containing:
                - url (str): The URL to make the GET request to
                
        Raises:
            ValueError: If the 'url' is not provided in the config
        """
        url = config.get("url")
        if not url:
            raise ValueError("Missing 'url' in config.")
        print(f"[HttpGetTask] GET {url}")
        response = requests.get(url)
        print(f"[HttpGetTask] Status: {response.status_code}")