import requests
from ..core import BaseTaskRunner


class HttpGetTask(BaseTaskRunner):
    type_name = "http_get"

    def run(self, config):
        url = config.get("url")
        if not url:
            raise ValueError("Missing 'url' in config.")
        print(f"[HttpGetTask] GET {url}")
        response = requests.get(url)
        print(f"[HttpGetTask] Status: {response.status_code}")
