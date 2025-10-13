import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Type
from enum import Enum

from ..models.task_model import TaskModel
from ..plugin_base import BaseTaskRunner
from ..utils.env_substitution import substitute_env_vars

# Set up logging
logger = logging.getLogger(__name__)

# Constants
MAX_PARALLEL_WORKERS = 10
TASK_SUCCESS = "success"
TASK_ERROR = "error"


class ExecutionStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


def format_task_tag(name):
    # Replace special characters with spaces and convert to uppercase
    return re.sub(r'[^a-zA-Z0-9]+', ' ', name).upper().strip()


def run_tasks_sequentially(tasks: List[TaskModel], plugins: Dict[str, Type[BaseTaskRunner]], verbose: bool = False):
    task_count = len(tasks)
    print(f"Running {task_count} tasks sequentially")

    for task in tasks:
        # Prepare task execution
        plugin_cls = plugins[task.type]
        runner = plugin_cls()

        # Substitute environment variables in config
        config = substitute_env_vars(task.config)

        # Log task execution
        _log_task_execution(task, config, verbose)

        # Execute task
        _execute_single_task(runner, task, config)


def run_tasks_in_parallel(tasks: List[TaskModel], plugins: Dict[str, Type[BaseTaskRunner]], verbose: bool = False):
    task_count = len(tasks)
    print(f"Running {task_count} tasks in parallel")

    # Submit all tasks to the executor
    futures = _submit_tasks_for_parallel_execution(tasks, plugins, verbose)

    # Process completed tasks
    _process_completed_tasks(futures)


def _log_task_execution(task, config, verbose):
    tag = format_task_tag(task.name)
    if verbose:
        print(f"[{tag}] [VERBOSE] Running {task.name} ({task.type}) with config: {config}")
    else:
        print(f"[{tag}] Running task: {task.name}")


def _execute_single_task(runner, task, config):
    tag = format_task_tag(task.name)
    try:
        runner.run(config)
        print(f"[{tag}] Task '{task.name}' completed successfully")
    except Exception as e:
        print(f"[{tag}] Task '{task.name}' failed: {e}")
        raise


def _submit_tasks_for_parallel_execution(tasks, plugins, verbose):
    futures = []
    worker_count = min(MAX_PARALLEL_WORKERS, len(tasks))

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        for task in tasks:
            plugin_cls = plugins[task.type]
            runner = plugin_cls()

            # Substitute environment variables in config
            config = substitute_env_vars(task.config)

            tag = format_task_tag(task.name)
            if verbose:
                print(f"[{tag}] [VERBOSE] Submitting {task.name} ({task.type}) for parallel execution")

            # Submit task to executor
            future = executor.submit(_run_single_task, task, runner, config, verbose)
            futures.append((future, task.name))

    return futures


def _process_completed_tasks(futures):
    for future, task_name in futures:
        try:
            result = future.result()
            _handle_task_result(result, task_name)
        except Exception as e:
            tag = format_task_tag(task_name)
            print(f"[{tag}] Task '{task_name}' failed with exception: {e}")


def _handle_task_result(result, task_name):
    tag = format_task_tag(task_name)
    if result is not None:
        status, message = result
        if status == TASK_SUCCESS:
            print(f"[{tag}] Task '{task_name}' completed successfully")
        else:
            print(f"[{tag}] Task '{task_name}' failed: {message}")
    else:
        print(f"[{tag}] Task '{task_name}' completed")


def _run_single_task(task: TaskModel, runner: BaseTaskRunner, config: Dict, verbose: bool):
    tag = format_task_tag(task.name)
    try:
        if verbose:
            print(f"[{tag}] [VERBOSE] Running {task.name} ({task.type}) with config: {config}")
        else:
            print(f"[{tag}] Running task: {task.name}")

        runner.run(config)
        return TASK_SUCCESS, None
    except Exception as e:
        return TASK_ERROR, str(e)
