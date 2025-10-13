import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Type

from ..models.task_model import TaskModel
from ..core import BaseTaskRunner
from ..utils.env_substitution import substitute_env_vars

# Set up logging
logger = logging.getLogger(__name__)


def run_tasks_sequentially(tasks: List[TaskModel], plugins: Dict[str, Type[BaseTaskRunner]], verbose: bool = False):
    print(f"Running {len(tasks)} tasks sequentially")

    for task in tasks:
        plugin_cls = plugins[task.type]
        runner = plugin_cls()

        # Substitute environment variables in config
        config = substitute_env_vars(task.config)

        if verbose:
            print(f"[Verbose] Running {task.name} ({task.type}) with config: {config}")
        else:
            print(f"Running task: {task.name}")

        try:
            runner.run(config)
            print(f"Task '{task.name}' completed successfully")
        except Exception as e:
            print(f"Task '{task.name}' failed: {e}")
            raise


def run_tasks_in_parallel(tasks: List[TaskModel], plugins: Dict[str, Type[BaseTaskRunner]], verbose: bool = False):
    """Run tasks in parallel using ThreadPoolExecutor."""
    print(f"Running {len(tasks)} tasks in parallel")

    # Create a list to store futures
    futures = []

    # Use ThreadPoolExecutor to run tasks in parallel
    with ThreadPoolExecutor(max_workers=min(10, len(tasks))) as executor:
        # Submit all tasks to the executor
        for task in tasks:
            plugin_cls = plugins[task.type]
            runner = plugin_cls()

            # Substitute environment variables in config
            config = substitute_env_vars(task.config)

            if verbose:
                print(f"[Verbose] Submitting {task.name} ({task.type}) for parallel execution")

            # Submit task to executor
            future = executor.submit(_run_single_task, task, runner, config, verbose)
            futures.append((future, task.name))

        # Process completed tasks
        for future, task_name in futures:
            try:
                result = future.result()
                if result is not None:
                    status, message = result
                    if status == "success":
                        print(f"Task '{task_name}' completed successfully")
                    else:
                        print(f"Task '{task_name}' failed: {message}")
                else:
                    print(f"Task '{task_name}' completed")
            except Exception as e:
                print(f"Task '{task_name}' failed with exception: {e}")


def _run_single_task(task: TaskModel, runner: BaseTaskRunner, config: Dict, verbose: bool):
    """Run a single task and return result status."""
    try:
        if verbose:
            print(f"[Verbose] Running {task.name} ({task.type}) with config: {config}")
        else:
            print(f"Running task: {task.name}")

        runner.run(config)
        return ("success", None)
    except Exception as e:
        return ("error", str(e))
