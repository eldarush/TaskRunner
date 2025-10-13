import click
import logging
from enum import Enum

from .utils.file_loader import load_tasks_from_file
from .utils.plugin_discovery import discover_plugins
from .tasks.executor import run_tasks_sequentially, run_tasks_in_parallel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_LOG_LEVEL = logging.INFO
DEBUG_LOG_LEVEL = logging.DEBUG
DRY_RUN_PREFIX = "[Dry Run]"
VALIDATION_SUCCESS_PREFIX = "Successfully validated"


class TaskRunnerMessages(Enum):
    WELCOME = "TaskRunner - A plugin-based task runner in Python."
    VERBOSE_ENABLED = "Verbose mode enabled"
    LOADED_TASKS = "Loaded {} tasks"
    FILTERED_TASKS = "Filtered to {} tasks (only='{}')"
    UNKNOWN_TASK_TYPE = "Unknown task type '{}' for task '{}'"
    NO_TASK_FOUND = "No task found with name '{}'"
    TASK_NAMES_MUST_BE_UNIQUE = "Task names must be unique"
    WOULD_RUN_TASKS = "{} Would run the following tasks:"
    AVAILABLE_PLUGINS = "Available plugins:"
    VALIDATION_FAILED = "Validation failed: {}"
    DUPLICATE_TASK_NAMES = "Duplicate task names found: {}"
    UNKNOWN_TASK_TYPES = "Unknown task types: {}"


@click.group()
def cli():
    """TaskRunner - A plugin-based task runner in Python."""
    pass


@cli.command()
@click.argument("file")
@click.option("--only", help="Run only a specific task by name")
@click.option("--verbose", is_flag=True, help="Show detailed logs")
@click.option("--dry-run", is_flag=True, help="Show what would run without executing")
@click.option("--parallel", is_flag=True, help="Run tasks in parallel")
@click.option("--plugin-prefix", help="Prefix for discovering plugins from installed packages")
def run(file, only, verbose, dry_run, parallel, plugin_prefix):
    """Run tasks from a JSON or YAML file."""
    if verbose:
        logging.getLogger().setLevel(DEBUG_LOG_LEVEL)
        logger.debug(TaskRunnerMessages.VERBOSE_ENABLED.value)

    try:
        # Discover plugins (local and optionally from installed packages)
        plugins = discover_plugins(package_prefix=plugin_prefix)
        tasks = load_tasks_from_file(file)

        # Check for duplicate task names
        task_names = [task.name for task in tasks]
        if len(task_names) != len(set(task_names)):
            raise ValueError(TaskRunnerMessages.TASK_NAMES_MUST_BE_UNIQUE.value)

        logger.debug(TaskRunnerMessages.LOADED_TASKS.value.format(len(tasks)))

        # Filter tasks if --only is specified
        if only:
            tasks = [task for task in tasks if task.name == only]
            if not tasks:
                raise ValueError(TaskRunnerMessages.NO_TASK_FOUND.value.format(only))
            logger.debug(TaskRunnerMessages.FILTERED_TASKS.value.format(len(tasks), only))

        # Validate all tasks before running
        for task in tasks:
            if task.type not in plugins:
                raise ValueError(TaskRunnerMessages.UNKNOWN_TASK_TYPE.value.format(task.type, task.name))

        if dry_run:
            print(TaskRunnerMessages.WOULD_RUN_TASKS.value.format(DRY_RUN_PREFIX))
            for task in tasks:
                print(f"  - {task.name} ({task.type})")
            return

        # Run tasks
        if parallel:
            run_tasks_in_parallel(tasks, plugins, verbose)
        else:
            run_tasks_sequentially(tasks, plugins, verbose)

    except Exception as e:
        error_message = f"Error: {e}"
        print(error_message)
        raise click.ClickException(str(e))


@cli.command()
@click.option("--plugin-prefix", help="Prefix for discovering plugins from installed packages")
def list_plugins(plugin_prefix):
    """List all available plugins."""
    plugins = discover_plugins(package_prefix=plugin_prefix)
    print(TaskRunnerMessages.AVAILABLE_PLUGINS.value)
    for name in plugins:
        print(f"  - {name}")


@cli.command()
@click.argument("file")
@click.option("--plugin-prefix", help="Prefix for discovering plugins from installed packages")
def validate(file, plugin_prefix):
    """Validate the given task file."""
    try:
        plugins = discover_plugins(package_prefix=plugin_prefix)
        tasks = load_tasks_from_file(file)

        # Check for duplicate task names
        task_names = [task.name for task in tasks]
        if len(task_names) != len(set(task_names)):
            duplicates = [name for name in task_names if task_names.count(name) > 1]
            raise ValueError(TaskRunnerMessages.DUPLICATE_TASK_NAMES.value.format(set(duplicates)))

        # Validate task types
        unknown_types = []
        for task in tasks:
            if task.type not in plugins:
                unknown_types.append(task.type)

        if unknown_types:
            raise ValueError(TaskRunnerMessages.UNKNOWN_TASK_TYPES.value.format(set(unknown_types)))

        print(f"{VALIDATION_SUCCESS_PREFIX} {len(tasks)} task(s)")
        for task in tasks:
            print(f"  - {task.name} ({task.type})")

    except Exception as e:
        error_message = f"{TaskRunnerMessages.VALIDATION_FAILED.value.format(e)}"
        print(error_message)
        raise click.ClickException(str(e))