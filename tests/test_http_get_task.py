import pytest
from unittest.mock import patch, MagicMock
import requests
from taskrunner.plugins.http_get_task import HttpGetTask, HttpGetTaskConfig


def test_http_get_task_config_creation():
    config_data = {"url": "https://example.com"}
    
    config = HttpGetTaskConfig(**config_data)
    
    assert config.url == "https://example.com"


def test_http_get_task_config_invalid_url_no_scheme():
    with pytest.raises(Exception):
        HttpGetTaskConfig(url="example.com")


def test_http_get_task_config_invalid_url_invalid_scheme():
    with pytest.raises(Exception):
        HttpGetTaskConfig(url="ftp://example.com")


def test_http_get_task_config_invalid_url_no_netloc():
    with pytest.raises(Exception):
        HttpGetTaskConfig(url="http://")


def test_http_get_task_config_missing_url():
    with pytest.raises(Exception):
        HttpGetTaskConfig()


def test_http_get_task_run_method():
    task = HttpGetTask()
    config = {"url": "https://example.com"}
    
    # Mock requests.get to avoid actual HTTP request
    mock_response = MagicMock()
    mock_response.status_code = 200
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            task.run(config)
            
            # Verify that requests.get was called with the correct URL
            mock_get.assert_called_once_with("https://example.com")
            
            # Verify that print was called with the expected messages
            assert mock_print.call_count == 2
            mock_print.assert_any_call("[HttpGetTask] GET https://example.com")
            mock_print.assert_any_call("[HttpGetTask] Status: 200")


def test_http_get_task_run_method_with_error_status():
    task = HttpGetTask()
    config = {"url": "https://example.com"}
    
    # Mock requests.get to return an error status
    mock_response = MagicMock()
    mock_response.status_code = 404
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            task.run(config)
            
            # Verify that requests.get was called with the correct URL
            mock_get.assert_called_once_with("https://example.com")
            
            # Verify that print was called with the expected messages
            assert mock_print.call_count == 2
            mock_print.assert_any_call("[HttpGetTask] GET https://example.com")
            mock_print.assert_any_call("[HttpGetTask] Status: 404")


def test_http_get_task_run_method_with_request_exception():
    task = HttpGetTask()
    config = {"url": "https://example.com"}
    
    # Mock requests.get to raise an exception
    with patch('requests.get', side_effect=requests.RequestException("Connection error")):
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            # Should raise the exception
            with pytest.raises(requests.RequestException):
                task.run(config)
            
            # Verify that print was called with the GET message but not the status message
            mock_print.assert_called_once_with("[HttpGetTask] GET https://example.com")