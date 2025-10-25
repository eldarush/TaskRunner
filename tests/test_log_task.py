from unittest.mock import patch

import pytest

from taskrunner.plugins.log_task import LogTask, LogTaskConfig


def test_log_task_config_creation():
    config_data = {"message": "Test message"}
    
    config = LogTaskConfig(**config_data)
    
    assert config.message == "Test message"


def test_log_task_config_missing_message():
    with pytest.raises(Exception):
        LogTaskConfig()


def test_log_task_run_method():
    task = LogTask()
    config = {"message": "Test log message"}
    
    # Mock print to capture output
    with patch('builtins.print') as mock_print:
        task.run(config)
        
        # Verify that print was called with the expected message
        mock_print.assert_called_once_with("[LogTask] Test log message")


def test_log_task_run_method_with_config_validation():
    task = LogTask()
    config = {"message": "Another test message"}
    
    # Mock print to capture output
    with patch('builtins.print') as mock_print:
        task.run(config)
        
        # Verify that print was called with the expected message
        mock_print.assert_called_once_with("[LogTask] Another test message")


def test_log_task_run_method_invalid_config():
    task = LogTask()
    config = {"invalid_field": "value"}
    
    with pytest.raises(Exception):
        task.run(config)