import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from taskrunner.utils.plugin_discovery import (
    discover_plugins, 
    _get_default_plugin_folder,
    _discover_local_plugins,
    _load_local_plugin_module,
    _discover_external_plugins,
    _register_plugin_classes,
    _is_valid_plugin_class
)
from taskrunner.plugin_base import BaseTaskRunner


def test_get_default_plugin_folder():
    # Mock os.path functions to return predictable values
    with patch('os.path.dirname') as mock_dirname, \
         patch('os.path.abspath') as mock_abspath, \
         patch('os.path.join') as mock_join:
        
        mock_abspath.return_value = '/fake/path/to/utils'
        mock_dirname.return_value = '/fake/path/to'
        mock_join.return_value = '/fake/path/to/plugins'
        
        result = _get_default_plugin_folder()
        
        assert result == '/fake/path/to/plugins'
        mock_abspath.assert_called_once()
        mock_dirname.assert_called_once_with('/fake/path/to/utils')
        mock_join.assert_called_once_with('/fake/path/to', '..', 'plugins')


def test_is_valid_plugin_class():
    # Test with BaseTaskRunner itself (should be False)
    assert _is_valid_plugin_class(BaseTaskRunner) is False
    
    # Test with a valid plugin class
    class TestPlugin(BaseTaskRunner):
        pass
    
    assert _is_valid_plugin_class(TestPlugin) is True
    
    # Test with a non-class object (should be False)
    assert _is_valid_plugin_class("not a class") is False
    
    # Test with a class that doesn't inherit from BaseTaskRunner (should be False)
    class NotAPlugin:
        pass
    
    assert _is_valid_plugin_class(NotAPlugin) is False


def test_register_plugin_classes():
    # Create a mock plugin class
    class MockPlugin(BaseTaskRunner):
        type_name = "mock"
    
    # Create a mock module with the plugin class
    mock_module = MagicMock()
    mock_module.__dict__ = {
        'MockPlugin': MockPlugin,
        '__name__': 'mock_module'
    }
    
    # Mock the dir function to return our class name
    with patch('taskrunner.utils.plugin_discovery.dir', return_value=['MockPlugin']):
        plugins = {}
        _register_plugin_classes(plugins, mock_module, "Found plugin: {}")
        
        assert "mock" in plugins
        assert plugins["mock"] == MockPlugin


def test_register_plugin_classes_no_type_name():
    # Create a mock plugin class without type_name
    class MockPlugin(BaseTaskRunner):
        pass  # No type_name attribute
    
    # Create a mock module with the plugin class
    mock_module = MagicMock()
    mock_module.__dict__ = {
        'MockPlugin': MockPlugin,
        '__name__': 'mock_module'
    }
    
    # Mock logging to capture warning
    with patch('taskrunner.utils.plugin_discovery.dir', return_value=['MockPlugin']), \
         patch('taskrunner.utils.plugin_discovery.logger') as mock_logger:
        
        plugins = {}
        _register_plugin_classes(plugins, mock_module, "Plugin class {} has no type_name")
        
        # Should be empty since the class has no type_name
        assert len(plugins) == 0
        mock_logger.warning.assert_called_once()


def test_load_local_plugin_module_success():
    # Create a mock plugin class
    class MockPlugin(BaseTaskRunner):
        type_name = "mock"
    
    # Mock importlib.import_module to return our mock plugin class
    with patch('taskrunner.utils.plugin_discovery.importlib.import_module') as mock_import_module, \
         patch('taskrunner.utils.plugin_discovery.logger'):
        
        # Create a mock module that returns our plugin class when accessed
        mock_module = MagicMock()
        mock_module.MockPlugin = MockPlugin
        mock_module.__name__ = 'taskrunner.plugins.mock_module'
        
        mock_import_module.return_value = mock_module
        plugins = {}
        _load_local_plugin_module(plugins, 'mock_module')
        
        assert "mock" in plugins
        assert plugins["mock"] == MockPlugin

def test_discover_local_plugins_folder_not_exists():
    # Mock os.path.exists to return False
    with patch('os.path.exists', return_value=False):
        plugins = {}
        _discover_local_plugins(plugins, '/nonexistent/folder')
        
        # Should be empty since folder doesn't exist
        assert len(plugins) == 0


def test_discover_plugins_default():
    # Mock the default plugin folder path
    with patch('taskrunner.utils.plugin_discovery._get_default_plugin_folder', 
               return_value='/fake/plugins'), \
         patch('os.path.exists', return_value=True), \
         patch('taskrunner.utils.plugin_discovery._discover_local_plugins') as mock_discover_local, \
         patch('taskrunner.utils.plugin_discovery._discover_external_plugins') as mock_discover_external:
        
        result = discover_plugins()
        
        # Should call local discovery but not external since no package_prefix
        mock_discover_local.assert_called_once()
        mock_discover_external.assert_not_called()
        
        assert isinstance(result, dict)


def test_discover_plugins_with_package_prefix():
    # Mock the default plugin folder path
    with patch('taskrunner.utils.plugin_discovery._get_default_plugin_folder', 
               return_value='/fake/plugins'), \
         patch('os.path.exists', return_value=True), \
         patch('taskrunner.utils.plugin_discovery._discover_local_plugins'), \
         patch('taskrunner.utils.plugin_discovery._discover_external_plugins') as mock_discover_external:
        
        result = discover_plugins(package_prefix='test.prefix')
        
        # Should call both local and external discovery
        mock_discover_external.assert_called_once()
        
        assert isinstance(result, dict)