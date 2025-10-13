"""
Core functionality for TaskRunner.

This module provides the core base class for plugins.
"""

import logging
from typing import Dict

# Set up logging
logger = logging.getLogger(__name__)

class BaseTaskRunner:
    """Base class for all plugins."""
    type_name: str = None  # Must be overridden

    def run(self, config: Dict):
        raise NotImplementedError("Plugins must implement 'run' method.")