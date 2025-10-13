# 🧩 TaskRunner – Plugin-Based Task Runner

A lightweight, extensible command-line tool that executes tasks defined in JSON or YAML files.

## 🚀 Quick Start

```bash
# Install TaskRunner
pip install -e .

# Run a simple example
taskrunner run examples/yaml/log_task_example.yaml

# List available plugins
taskrunner list-plugins
```

## 🧱 Task Definition

Tasks are defined in JSON or YAML files as a list of task objects:

```yaml
- name: welcome_message
  type: log
  config:
    message: "Welcome to TaskRunner!"
```

Each task has:
- `name`: A unique identifier
- `type`: The plugin type to execute
- `config`: Configuration specific to the task type

## 🕹️ CLI Commands

```bash
# Run tasks
taskrunner run <file> [--only <task_name>] [--dry-run] [--verbose] [--parallel]

# Validate task file
taskrunner validate <file>

# List available plugins
taskrunner list-plugins
```

## 🔧 Built-in Plugins

- **`log`** - Print messages to console
- **`wait`** - Pause execution for specified time
- **`http_get`** - Make HTTP GET requests
- **`file`** - Create or delete files

## 🧩 Adding New Plugins

Create a new file in `taskrunner/plugins/` that subclasses `BaseTaskRunner`:

```python
from taskrunner.plugin_base import BaseTaskRunner

class MyTask(BaseTaskRunner):
    type_name = "my_task"

    def run(self, config):
        print(f"Running my custom task with config: {config}")
```

The plugin is automatically discovered.

## ⚙️ Advanced Features

### Environment Variables

Use `${VAR_NAME}` syntax for environment variable substitution:

```yaml
- name: env_example
  type: log
  config:
    message: "Environment: ${ENV_NAME}"
```

### Parallel Execution

Run tasks in parallel:
```bash
taskrunner run <file> --parallel
```

## 📁 Project Structure

```
taskrunner/
├── cli.py          # Command-line interface
├── plugin_base.py  # Base plugin class
├── plugins/        # Built-in plugins
├── models/         # Data models
├── tasks/          # Task execution logic
└── utils/          # Utility functions
```