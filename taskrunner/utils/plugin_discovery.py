import importlib
import os
import pkgutil
import logging
import sys
from typing import Dict, Type
from enum import Enum

from ..core import BaseTaskRunner

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_PLUGINS_DIR = "plugins"
MODULE_PREFIX = "taskrunner.plugins."
PLUGIN_CLASS_NAME_WARNING = "Plugin class {} has no type_name"
PLUGIN_FOUND_MESSAGE = "Found plugin: {}"
PLUGIN_EXTERNAL_FOUND_MESSAGE = "Found external plugin: {}"
PLUGIN_IMPORT_ERROR = "Error loading plugin module {}: {}"
PLUGIN_EXTERNAL_IMPORT_ERROR = "Error loading plugin from module {}: {}"
PLUGIN_PACKAGES_ERROR = "Error discovering plugins from packages: {}"


class PluginDiscoveryMessages(Enum):
    DISCOVERING_PLUGINS = "Discovering plugins in {}"
    IMPORTING_MODULE = "Importing module {}"
    DISCOVERING_EXTERNAL = "Discovering plugins from packages with prefix '{}'"
    CHECKING_MODULE = "Checking module {} for plugins"


def discover_plugins(plugin_folder: str = None, package_prefix: str = None) -> Dict[str, Type[BaseTaskRunner]]:
    """Dynamically discover all plugin classes."""
    plugins = {}

    # If no plugin folder specified, use the default plugins directory
    if plugin_folder is None:
        plugin_folder = _get_default_plugin_folder()

    logger.debug(PluginDiscoveryMessages.DISCOVERING_PLUGINS.value.format(plugin_folder))

    # Check if the plugin folder exists and discover plugins
    _discover_local_plugins(plugins, plugin_folder)

    # Discover plugins from installed packages if package_prefix is provided
    if package_prefix:
        _discover_external_plugins(plugins, package_prefix)

    return plugins


def _get_default_plugin_folder():
    """Get the default plugins directory path."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", DEFAULT_PLUGINS_DIR)


def _discover_local_plugins(plugins, plugin_folder):
    """Discover local plugins in the specified folder."""
    if not os.path.exists(plugin_folder):
        return

    # Add plugin folder to sys.path if it's not already there
    if plugin_folder not in sys.path:
        sys.path.insert(0, plugin_folder)

    # Discover plugins in the folder
    for _, module_name, _ in pkgutil.iter_modules([plugin_folder]):
        _load_local_plugin_module(plugins, module_name)


def _load_local_plugin_module(plugins, module_name):
    """Load a local plugin module and register its plugins."""
    try:
        full_module_name = f"{MODULE_PREFIX}{module_name}"
        logger.debug(PluginDiscoveryMessages.IMPORTING_MODULE.value.format(full_module_name))
        module = importlib.import_module(full_module_name)
        _register_plugin_classes(plugins, module, PLUGIN_FOUND_MESSAGE)
    except Exception as e:
        logger.error(PLUGIN_IMPORT_ERROR.format(module_name, e))


def _discover_external_plugins(plugins, package_prefix):
    """Discover external plugins from installed packages."""
    logger.debug(PluginDiscoveryMessages.DISCOVERING_EXTERNAL.value.format(package_prefix))
    
    try:
        package = importlib.import_module(package_prefix)
        if hasattr(package, '__path__'):
            _discover_plugins_in_package(plugins, package)
        else:
            _discover_plugins_in_module(plugins, package)
    except ImportError:
        _discover_plugins_fallback(plugins, package_prefix)
    except Exception as e:
        logger.error(PLUGIN_PACKAGES_ERROR.format(e))


def _discover_plugins_in_package(plugins, package):
    """Discover plugins in a package."""
    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            logger.debug(PluginDiscoveryMessages.CHECKING_MODULE.value.format(modname))
            module = importlib.import_module(modname)
            _register_plugin_classes(plugins, module, PLUGIN_EXTERNAL_FOUND_MESSAGE, avoid_overwrite=True)
        except Exception as e:
            logger.error(PLUGIN_EXTERNAL_IMPORT_ERROR.format(modname, e))


def _discover_plugins_in_module(plugins, package):
    """Discover plugins directly in a module."""
    _register_plugin_classes(plugins, package, PLUGIN_EXTERNAL_FOUND_MESSAGE, avoid_overwrite=True)


def _discover_plugins_fallback(plugins, package_prefix):
    """Fallback method for discovering plugins."""
    for importer, modname, ispkg in pkgutil.iter_modules():
        if modname.startswith(package_prefix):
            try:
                logger.debug(PluginDiscoveryMessages.CHECKING_MODULE.value.format(modname))
                module = importlib.import_module(modname)
                _register_plugin_classes(plugins, module, PLUGIN_EXTERNAL_FOUND_MESSAGE, avoid_overwrite=True)
            except Exception as e:
                logger.error(PLUGIN_EXTERNAL_IMPORT_ERROR.format(modname, e))


def _register_plugin_classes(plugins, module, found_message, avoid_overwrite=False):
    """Register plugin classes from a module."""
    for attr in dir(module):
        obj = getattr(module, attr)
        if not _is_valid_plugin_class(obj):
            continue
            
        if not obj.type_name:
            logger.warning(PLUGIN_CLASS_NAME_WARNING.format(obj.__name__))
            continue
            
        # Avoid overwriting local plugins with the same type_name for external plugins
        if avoid_overwrite and obj.type_name in plugins:
            continue
            
        plugins[obj.type_name] = obj
        logger.debug(found_message.format(obj.type_name))


def _is_valid_plugin_class(obj):
    """Check if an object is a valid plugin class."""
    return (isinstance(obj, type) and 
            issubclass(obj, BaseTaskRunner) and 
            obj is not BaseTaskRunner)