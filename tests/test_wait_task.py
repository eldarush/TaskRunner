from unittest.mock import patch

import pytest

from taskrunner.plugins.wait_task import WaitTask, WaitTaskConfig


def test_wait_task_config_creation():
    config_data = {"seconds": 5}
    
    config = WaitTaskConfig(**config_data)
    
    assert config.seconds == 5


def test_wait_task_config_invalid_seconds_negative():
    with pytest.raises(Exception):
        WaitTaskConfig(seconds=-1)


def test_wait_task_config_invalid_seconds_too_large():
    with pytest.raises(Exception):
        WaitTaskConfig(seconds=3601)


def test_wait_task_config_missing_seconds():
    with pytest.raises(Exception):
        WaitTaskConfig()


def test_wait_task_run_method():
    task = WaitTask()
    config = {"seconds": 2}
    
    # Mock time.sleep to avoid actual waiting
    with patch('time.sleep') as mock_sleep:
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            task.run(config)
            
            # Verify that sleep was called with the correct duration
            mock_sleep.assert_called_once_with(2)
            
            # Verify that print was called with the expected messages
            assert mock_print.call_count == 2
            mock_print.assert_any_call("[WaitTask] Waiting 2 seconds...")
            mock_print.assert_any_call("[WaitTask] Done.")


def test_wait_task_run_method_zero_seconds():
    task = WaitTask()
    config = {"seconds": 0}
    
    # Mock time.sleep to avoid actual waiting
    with patch('time.sleep') as mock_sleep:
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            task.run(config)
            
            # Verify that sleep was called with 0
            mock_sleep.assert_called_once_with(0)
            
            # Verify that print was called with the expected messages
            assert mock_print.call_count == 2
            mock_print.assert_any_call("[WaitTask] Waiting 0 seconds...")
            mock_print.assert_any_call("[WaitTask] Done.")