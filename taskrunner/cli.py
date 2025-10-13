"""
Command Line Interface for TaskRunner.

This module provides the command line interface for TaskRunner using Click.
It includes commands for running tasks, validating task files, and listing plugins.
"""

import click
import logging

from .utils.file_loader import load_tasks_from_file
from .utils.plugin_discovery import discover_plugins
from .tasks.executor import run_tasks_sequentially, run_tasks_in_parallel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    try:
        # Discover plugins (local and optionally from installed packages)
        plugins = discover_plugins(package_prefix=plugin_prefix)
        tasks = load_tasks_from_file(file)
        
        # Check for duplicate task names
        task_names = [task.name for task in tasks]
        if len(task_names) != len(set(task_names)):
            raise ValueError("Task names must be unique")
        
        logger.debug(f"Loaded {len(tasks)} tasks")
        
        # Filter tasks if --only is specified
        if only:
            tasks = [task for task in tasks if task.name == only]
            if not tasks:
                raise ValueError(f"No task found with name '{only}'")
            logger.debug(f"Filtered to {len(tasks)} tasks (only='{only}')")
        
        # Validate all tasks before running
        for task in tasks:
            if task.type not in plugins:
                raise ValueError(f"Unknown task type '{task.type}' for task '{task.name}'")
        
        if dry_run:
            print("[Dry Run] Would run the following tasks:")
            for task in tasks:
                print(f"  - {task.name} ({task.type})")
            return
        
        # Run tasks
        if parallel:
            run_tasks_in_parallel(tasks, plugins, verbose)
        else:
            run_tasks_sequentially(tasks, plugins, verbose)
        
    except Exception as e:
        print(f"Error: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.option("--plugin-prefix", help="Prefix for discovering plugins from installed packages")
def list_plugins(plugin_prefix):
    """List all available plugins."""
    plugins = discover_plugins(package_prefix=plugin_prefix)
    print("Available plugins:")
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
            raise ValueError(f"Duplicate task names found: {set(duplicates)}")
        
        # Validate task types
        unknown_types = []
        for task in tasks:
            if task.type not in plugins:
                unknown_types.append(task.type)
        
        if unknown_types:
            raise ValueError(f"Unknown task types: {set(unknown_types)}")
        
        print(f"Successfully validated {len(tasks)} task(s)")
        for task in tasks:
            print(f"  - {task.name} ({task.type})")
            
    except Exception as e:
        print(f"Validation failed: {e}")
        raise click.ClickException(str(e))

if __name__ == "__main__":
    cli()