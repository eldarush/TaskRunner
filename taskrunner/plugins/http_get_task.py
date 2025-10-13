import requests
from ..plugin_base import BaseTaskRunner
from pydantic import BaseModel, Field, validator
from urllib.parse import urlparse


class HttpGetTaskConfig(BaseModel):
    url: str = Field(..., description="The URL to make the GET request to")

    @validator('url')
    def validate_url(cls, v):
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError('Invalid URL format')
        if parsed.scheme not in ['http', 'https']:
            raise ValueError('URL must use http or https scheme')
        return v


class HttpGetTask(BaseTaskRunner):
    type_name = "http_get"

    def run(self, config):
        # Validate config using Pydantic model
        validated_config = HttpGetTaskConfig(**config)
        print(f"[HttpGetTask] GET {validated_config.url}")
        response = requests.get(validated_config.url)
        print(f"[HttpGetTask] Status: {response.status_code}")