from unittest.mock import patch, mock_open

import pytest
from pydantic import ValidationError

from taskrunner.plugins.file_task import FileTask, FileTaskConfig, FileAction


def test_file_task_config_create_action():
    config_data = {
        "action": "create",
        "path": "/tmp/test.txt",
        "content": "Hello, World!"
    }
    
    config = FileTaskConfig(**config_data)
    
    assert config.action == FileAction.CREATE
    assert config.path == "/tmp/test.txt"
    assert config.content == "Hello, World!"


def test_file_task_config_delete_action():
    config_data = {
        "action": "delete",
        "path": "/tmp/test.txt"
    }
    
    config = FileTaskConfig(**config_data)
    
    assert config.action == FileAction.DELETE
    assert config.path == "/tmp/test.txt"
    assert config.content == ""  # Default value


def test_file_task_config_missing_required_fields():
    # Missing action
    with pytest.raises(Exception):
        FileTaskConfig(path="/tmp/test.txt")
    
    # Missing path
    with pytest.raises(Exception):
        FileTaskConfig(action="create")


def test_file_task_config_invalid_action():
    with pytest.raises(ValidationError):
        FileTaskConfig(action="invalid", path="/tmp/test.txt")


def test_file_task_run_create_action():
    task = FileTask()
    config = {
        "action": "create",
        "path": "/tmp/test.txt",
        "content": "Test content"
    }
    
    # Mock open using mock_open
    with patch('builtins.open', mock_open()) as mock_file:
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            task.run(config)
            
            # Verify that open was called with the correct parameters
            mock_file.assert_called_once_with("/tmp/test.txt", "w")
            
            # Verify that write was called with the correct content
            handle = mock_file()
            handle.write.assert_called_once_with("Test content")
            
            # Verify that print was called with the expected messages
            assert mock_print.call_count == 2
            mock_print.assert_any_call("[FileTask] Creating file /tmp/test.txt")
            mock_print.assert_any_call("[FileTask] File /tmp/test.txt created successfully")


def test_file_task_run_create_action_empty_content():
    task = FileTask()
    config = {
        "action": "create",
        "path": "/tmp/test.txt"
    }
    
    # Mock open using mock_open
    with patch('builtins.open', mock_open()) as mock_file:
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            task.run(config)
            
            # Verify that open was called with the correct parameters
            mock_file.assert_called_once_with("/tmp/test.txt", "w")
            
            # Verify that write was called with empty string
            handle = mock_file()
            handle.write.assert_called_once_with("")
            
            # Verify that print was called with the expected messages
            assert mock_print.call_count == 2
            mock_print.assert_any_call("[FileTask] Creating file /tmp/test.txt")
            mock_print.assert_any_call("[FileTask] File /tmp/test.txt created successfully")


def test_file_task_run_delete_action_existing_file():
    task = FileTask()
    config = {
        "action": "delete",
        "path": "/tmp/test.txt"
    }
    
    # Mock os.path.exists to return True and os.remove for file deletion
    with patch('os.path.exists', return_value=True) as mock_exists:
        with patch('os.remove') as mock_remove:
            # Mock print to capture output
            with patch('builtins.print') as mock_print:
                task.run(config)
                
                # Verify that os.path.exists was called with the correct path
                mock_exists.assert_called_once_with("/tmp/test.txt")
                
                # Verify that os.remove was called with the correct path
                mock_remove.assert_called_once_with("/tmp/test.txt")
                
                # Verify that print was called with the expected messages
                assert mock_print.call_count == 2
                mock_print.assert_any_call("[FileTask] Deleting file /tmp/test.txt")
                mock_print.assert_any_call("[FileTask] File /tmp/test.txt deleted successfully")


def test_file_task_run_delete_action_nonexistent_file():
    task = FileTask()
    config = {
        "action": "delete",
        "path": "/tmp/nonexistent.txt"
    }
    
    # Mock os.path.exists to return False
    with patch('os.path.exists', return_value=False) as mock_exists:
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            task.run(config)
            
            # Verify that os.path.exists was called with the correct path
            mock_exists.assert_called_once_with("/tmp/nonexistent.txt")
            
            # Verify that os.remove was not called
            # Verify that print was called with the expected message
            mock_print.assert_called_once_with("[FileTask] File /tmp/nonexistent.txt does not exist")


def test_file_task_run_invalid_action():
    task = FileTask()
    config = {
        "action": "invalid",  # This will cause a ValidationError during config validation
        "path": "/tmp/test.txt"
    }
    
    with pytest.raises(ValidationError):
        task.run(config)