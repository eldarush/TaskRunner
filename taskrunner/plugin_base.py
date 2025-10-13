import logging
from typing import Dict
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)


class CoreMessages(Enum):
    NOT_IMPLEMENTED_ERROR = "Plugins must implement 'run' method."


class BaseTaskRunner:
    """Base class for all plugins."""
    type_name: str = None  # Must be overridden

    def run(self, config: Dict):
        raise NotImplementedError(CoreMessages.NOT_IMPLEMENTED_ERROR.value)
