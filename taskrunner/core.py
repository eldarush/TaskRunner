import logging
from typing import Dict

# Set up logging
logger = logging.getLogger(__name__)


class BaseTaskRunner:
    type_name: str = None  # Must be overridden

    def run(self, config: Dict):
        raise NotImplementedError("Plugins must implement 'run' method.")
