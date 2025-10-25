from unittest.mock import patch, MagicMock

import pytest

from taskrunner.models.task_model import TaskModel
from taskrunner.tasks.executor import (
    run_tasks_sequentially,
    run_tasks_in_parallel,
    _get_cpu_count,
    format_task_tag,
    _log_task_execution,
    _execute_single_task,
    _submit_tasks_for_parallel_execution,
    _process_completed_tasks,
    _handle_task_result,
    _run_single_task
)


def test_get_cpu_count():
    # Test when os.cpu_count is available
    with patch('os.cpu_count', return_value=8):
        result = _get_cpu_count()
        assert result == 8
    
    # Test when os.cpu_count returns None or 0
    with patch('os.cpu_count', return_value=None):
        result = _get_cpu_count()
        assert result == 4  # Default fallback
    
    with patch('os.cpu_count', return_value=0):
        result = _get_cpu_count()
        assert result == 4  # Default fallback


def test_format_task_tag():
    # Test normal name
    assert format_task_tag("test_task") == "TEST TASK"
    
    # Test name with special characters
    assert format_task_tag("test-task_1") == "TEST TASK 1"
    
    # Test name with multiple special characters
    assert format_task_tag("test---task___1") == "TEST TASK 1"
    
    # Test name with leading/trailing spaces after formatting
    assert format_task_tag("  test_task  ") == "TEST TASK"


def test_run_tasks_sequentially():
    # Create mock tasks
    task1 = TaskModel(name="task1", type="log", config={"message": "Hello"})
    task2 = TaskModel(name="task2", type="wait", config={"seconds": 1})
    tasks = [task1, task2]
    
    # Create mock plugins
    mock_log_plugin = MagicMock()
    mock_wait_plugin = MagicMock()
    plugins = {
        "log": mock_log_plugin,
        "wait": mock_wait_plugin
    }
    
    # Mock the helper functions
    with patch('taskrunner.tasks.executor._log_task_execution') as mock_log_execution, \
         patch('taskrunner.tasks.executor._execute_single_task') as mock_execute_single, \
         patch('taskrunner.tasks.executor.substitute_env_vars', side_effect=lambda x: x):
        
        run_tasks_sequentially(tasks, plugins, verbose=False)
        
        # Verify that the functions were called the correct number of times
        assert mock_log_execution.call_count == 2
        assert mock_execute_single.call_count == 2
        
        # Verify that tasks were processed in order
        first_call_args = mock_execute_single.call_args_list[0][0]
        second_call_args = mock_execute_single.call_args_list[1][0]
        
        assert first_call_args[1].name == "task1"
        assert second_call_args[1].name == "task2"


def test_run_tasks_in_parallel():
    # Create mock tasks
    task1 = TaskModel(name="task1", type="log", config={"message": "Hello"})
    task2 = TaskModel(name="task2", type="wait", config={"seconds": 1})
    tasks = [task1, task2]
    
    # Create mock plugins
    mock_log_plugin = MagicMock()
    mock_wait_plugin = MagicMock()
    plugins = {
        "log": mock_log_plugin,
        "wait": mock_wait_plugin
    }
    
    # Mock the helper functions
    with patch('taskrunner.tasks.executor._submit_tasks_for_parallel_execution') as mock_submit, \
         patch('taskrunner.tasks.executor._process_completed_tasks') as mock_process:
        
        # Mock the return value of _submit_tasks_for_parallel_execution
        mock_submit.return_value = [("future1", "task1"), ("future2", "task2")]
        
        run_tasks_in_parallel(tasks, plugins, verbose=False)
        
        # Verify that the functions were called
        mock_submit.assert_called_once_with(tasks, plugins, False)
        mock_process.assert_called_once_with([("future1", "task1"), ("future2", "task2")])


def test_submit_tasks_for_parallel_execution():
    # Create mock tasks
    task1 = TaskModel(name="task1", type="log", config={"message": "Hello"})
    task2 = TaskModel(name="task2", type="wait", config={"seconds": 1})
    tasks = [task1, task2]
    
    # Create mock plugins
    mock_log_plugin = MagicMock()
    mock_wait_plugin = MagicMock()
    plugins = {
        "log": mock_log_plugin,
        "wait": mock_wait_plugin
    }
    
    # Mock ThreadPoolExecutor
    with patch('taskrunner.tasks.executor.ThreadPoolExecutor') as mock_executor_class, \
         patch('taskrunner.tasks.executor.substitute_env_vars', side_effect=lambda x: x), \
         patch('taskrunner.tasks.executor._run_single_task') as mock_run_single, \
         patch('taskrunner.tasks.executor.format_task_tag', return_value="TASK"):
        
        # Create a mock executor instance
        mock_executor_instance = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor_instance
        
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            result = _submit_tasks_for_parallel_execution(tasks, plugins, verbose=False)
            
            # Verify that executor.submit was called for each task
            assert mock_executor_instance.submit.call_count == 2
            
            # Verify that we got the expected result format
            assert len(result) == 2
            assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


def test_process_completed_tasks():
    # Create mock futures
    mock_future1 = MagicMock()
    mock_future2 = MagicMock()
    mock_future3 = MagicMock()
    
    # Configure the futures to return different results
    mock_future1.result.return_value = ("success", None)
    mock_future2.result.return_value = ("error", "Something went wrong")
    mock_future3.result.side_effect = Exception("Task failed")
    
    futures = [
        (mock_future1, "task1"),
        (mock_future2, "task2"),
        (mock_future3, "task3")
    ]
    
    # Mock the helper function
    with patch('taskrunner.tasks.executor._handle_task_result') as mock_handle_result, \
         patch('taskrunner.tasks.executor.format_task_tag', return_value="TASK"), \
         patch('builtins.print') as mock_print:
        
        _process_completed_tasks(futures)
        
        # Verify that successful results are passed to _handle_task_result
        mock_handle_result.assert_any_call(("success", None), "task1")
        
        # Verify that exceptions are caught and printed (should be 1 call for the exception)
        assert mock_print.call_count == 1


def test_handle_task_result():
    with patch('taskrunner.tasks.executor.format_task_tag', return_value="TASK"), \
         patch('builtins.print') as mock_print:
        
        # Test success result
        _handle_task_result(("success", None), "test_task")
        mock_print.assert_called_with("[TASK] Task 'test_task' completed successfully")
        
        # Reset mock
        mock_print.reset_mock()
        
        # Test error result
        _handle_task_result(("error", "Error message"), "test_task")
        mock_print.assert_called_with("[TASK] Task 'test_task' failed: Error message")
        
        # Reset mock
        mock_print.reset_mock()
        
        # Test None result
        _handle_task_result(None, "test_task")
        mock_print.assert_called_with("[TASK] Task 'test_task' completed")


def test_run_single_task():
    # Create a mock task
    task = TaskModel(name="test_task", type="log", config={"message": "Hello"})
    
    # Create a mock runner
    mock_runner = MagicMock()
    
    # Mock the helper functions
    with patch('taskrunner.tasks.executor.format_task_tag', return_value="TEST TASK"), \
         patch('builtins.print') as mock_print:
        
        # Test successful execution with verbose=False
        result = _run_single_task(task, mock_runner, {"message": "Hello"}, verbose=False)
        
        # Verify that runner.run was called
        mock_runner.run.assert_called_once_with({"message": "Hello"})
        
        # Verify that the correct success result is returned
        assert result == ("success", None)
        
        # Verify that print was called for task execution
        mock_print.assert_called_with("[TEST TASK] Running task: test_task")


def test_run_single_task_with_exception():
    # Create a mock task
    task = TaskModel(name="test_task", type="log", config={"message": "Hello"})
    
    # Create a mock runner that raises an exception
    mock_runner = MagicMock()
    mock_runner.run.side_effect = Exception("Task failed")
    
    # Mock the helper functions
    with patch('taskrunner.tasks.executor.format_task_tag', return_value="TEST TASK"), \
         patch('builtins.print') as mock_print:
        
        # Test exception handling
        result = _run_single_task(task, mock_runner, {"message": "Hello"}, verbose=False)
        
        # Verify that the correct error result is returned
        assert result == ("error", "Task failed")


def test_log_task_execution():
    # Create a mock task
    task = TaskModel(name="test_task", type="log", config={"message": "Hello"})
    
    with patch('taskrunner.tasks.executor.format_task_tag', return_value="TEST TASK"), \
         patch('builtins.print') as mock_print:
        
        # Test verbose logging
        _log_task_execution(task, {"message": "Hello"}, verbose=True)
        mock_print.assert_called_with("[TEST TASK] [VERBOSE] Running test_task (log) with config: {'message': 'Hello'}")
        
        # Reset mock
        mock_print.reset_mock()
        
        # Test non-verbose logging
        _log_task_execution(task, {"message": "Hello"}, verbose=False)
        mock_print.assert_called_with("[TEST TASK] Running task: test_task")


def test_execute_single_task():
    # Create a mock task
    task = TaskModel(name="test_task", type="log", config={"message": "Hello"})
    
    # Create a mock runner
    mock_runner = MagicMock()
    
    with patch('taskrunner.tasks.executor.format_task_tag', return_value="TEST TASK"), \
         patch('builtins.print') as mock_print:
        
        # Test successful execution
        _execute_single_task(mock_runner, task, {"message": "Hello"})
        
        # Verify that runner.run was called
        mock_runner.run.assert_called_once_with({"message": "Hello"})
        
        # Verify that success message was printed
        mock_print.assert_called_with("[TEST TASK] Task 'test_task' completed successfully")


def test_execute_single_task_with_exception():
    # Create a mock task
    task = TaskModel(name="test_task", type="log", config={"message": "Hello"})
    
    # Create a mock runner that raises an exception
    mock_runner = MagicMock()
    mock_runner.run.side_effect = Exception("Task failed")
    
    with patch('taskrunner.tasks.executor.format_task_tag', return_value="TEST TASK"), \
         patch('builtins.print') as mock_print:
        
        # Test exception handling
        with pytest.raises(Exception, match="Task failed"):
            _execute_single_task(mock_runner, task, {"message": "Hello"})
        
        # Verify that error message was printed
        mock_print.assert_called_with("[TEST TASK] Task 'test_task' failed: Task failed")