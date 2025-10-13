"""
Plugin discovery for TaskRunner.

This module provides functionality for discovering plugins.
"""

import importlib
import os
import pkgutil
import logging
from typing import Dict, Type

from ..core import BaseTaskRunner

# Set up logging
logger = logging.getLogger(__name__)

def discover_plugins(plugin_folder: str = None, package_prefix: str = None) -> Dict[str, Type[BaseTaskRunner]]:
    """Dynamically discover all plugin classes.
    
    Args:
        plugin_folder (str, optional): Path to local plugins directory
        package_prefix (str, optional): Prefix for discovering plugins from installed packages
        
    Returns:
        Dict[str, Type[BaseTaskRunner]]: Dictionary mapping plugin type names to plugin classes
    """
    plugins = {}
    
    # If no plugin folder specified, use the default plugins directory
    if plugin_folder is None:
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        plugin_folder = os.path.join(current_dir, "..", "plugins")
    
    logger.debug(f"Discovering plugins in {plugin_folder}")
    
    # Check if the plugin folder exists
    if os.path.exists(plugin_folder):
        # Add plugin folder to sys.path if it's not already there
        import sys
        if plugin_folder not in sys.path:
            sys.path.insert(0, plugin_folder)
        
        # Discover plugins in the folder
        for _, module_name, _ in pkgutil.iter_modules([plugin_folder]):
            try:
                # Dynamically import the modules from the plugins package
                full_module_name = f"taskrunner.plugins.{module_name}"
                logger.debug(f"Importing module {full_module_name}")
                module = importlib.import_module(full_module_name)
                
                # Look for plugin classes
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if (isinstance(obj, type) and 
                        issubclass(obj, BaseTaskRunner) and 
                        obj is not BaseTaskRunner):
                        if not obj.type_name:
                            logger.warning(f"Plugin class {obj.__name__} has no type_name")
                            continue
                        plugins[obj.type_name] = obj
                        logger.debug(f"Found plugin: {obj.type_name}")
            except Exception as e:
                logger.error(f"Error loading plugin module {module_name}: {e}")
    
    # Discover plugins from installed packages if package_prefix is provided
    if package_prefix:
        logger.debug(f"Discovering plugins from packages with prefix '{package_prefix}'")
        try:
            # Try to import the package directly
            try:
                package = importlib.import_module(package_prefix)
                # If it's a package, look for plugins in its modules
                if hasattr(package, '__path__'):
                    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                        try:
                            logger.debug(f"Checking module {modname} for plugins")
                            module = importlib.import_module(modname)
                            
                            # Look for plugin classes in the module
                            for attr in dir(module):
                                obj = getattr(module, attr)
                                if (isinstance(obj, type) and 
                                    issubclass(obj, BaseTaskRunner) and 
                                    obj is not BaseTaskRunner):
                                    if not obj.type_name:
                                        logger.warning(f"Plugin class {obj.__name__} has no type_name")
                                        continue
                                    # Avoid overwriting local plugins with the same type_name
                                    if obj.type_name not in plugins:
                                        plugins[obj.type_name] = obj
                                        logger.debug(f"Found external plugin: {obj.type_name}")
                        except Exception as e:
                            logger.error(f"Error loading plugin from module {modname}: {e}")
                else:
                    # If it's a module, look for plugin classes directly
                    for attr in dir(package):
                        obj = getattr(package, attr)
                        if (isinstance(obj, type) and 
                            issubclass(obj, BaseTaskRunner) and 
                            obj is not BaseTaskRunner):
                            if not obj.type_name:
                                logger.warning(f"Plugin class {obj.__name__} has no type_name")
                                continue
                            # Avoid overwriting local plugins with the same type_name
                            if obj.type_name not in plugins:
                                plugins[obj.type_name] = obj
                                logger.debug(f"Found external plugin: {obj.type_name}")
            except ImportError:
                # If direct import fails, try the original approach
                # Discover plugins from installed packages
                for importer, modname, ispkg in pkgutil.iter_modules():
                    if modname.startswith(package_prefix):
                        try:
                            logger.debug(f"Checking module {modname} for plugins")
                            module = importlib.import_module(modname)
                            
                            # Look for plugin classes in the module
                            for attr in dir(module):
                                obj = getattr(module, attr)
                                if (isinstance(obj, type) and 
                                    issubclass(obj, BaseTaskRunner) and 
                                    obj is not BaseTaskRunner):
                                    if not obj.type_name:
                                        logger.warning(f"Plugin class {obj.__name__} has no type_name")
                                        continue
                                    # Avoid overwriting local plugins with the same type_name
                                    if obj.type_name not in plugins:
                                        plugins[obj.type_name] = obj
                                        logger.debug(f"Found external plugin: {obj.type_name}")
                        except Exception as e:
                            logger.error(f"Error loading plugin from module {modname}: {e}")
        except Exception as e:
            logger.error(f"Error discovering plugins from packages: {e}")
    
    return plugins