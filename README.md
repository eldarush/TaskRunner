# 🧩 TaskRunner – Plugin-Based Task Runner in Python

TaskRunner is a lightweight, extensible command-line tool that executes tasks defined in JSON or YAML files. It's built around a plugin architecture that allows you to add new task types without modifying the core code.

## 🚀 Quick Start

```bash
# Install TaskRunner
pip install -e .

# Or install dependencies separately
pip install -r requirements.txt
pip install -e .

# Run a simple example
taskrunner run examples/yaml/log_task_example.yaml

# List available plugins
taskrunner list-plugins
```

## 🧱 Task Definition

Tasks are defined in JSON or YAML files as a list of task objects. Each task has:
- `name`: A unique identifier for the task
- `type`: The plugin type to execute
- `config`: Configuration specific to the task type

Example:
```yaml
- name: welcome_message
  type: log
  config:
    message: "Welcome to TaskRunner!"
```

## 🕹️ CLI Commands

```bash
# Run tasks
taskrunner run <file> [--only <task_name>] [--dry-run] [--verbose] [--parallel]

# Validate task file
taskrunner validate <file>

# List available plugins
taskrunner list-plugins [--plugin-prefix <prefix>]
```

## 🔧 Built-in Plugins

- **`log`** - Print messages to the console
- **`wait`** - Pause execution for a specified time
- **`http_get`** - Make HTTP GET requests
- **`file`** - Create or delete files

## 🧩 Adding New Plugins

Create a new file in `taskrunner/plugins/` that subclasses `BaseTaskRunner`:

```python
from taskrunner.core import BaseTaskRunner

class MyTask(BaseTaskRunner):
    type_name = "my_task"

    def run(self, config):
        # Your implementation here
        print(f"Running my custom task with config: {config}")
```

The plugin is automatically discovered and available for use in task files.

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

Run tasks in parallel with the `--parallel` flag:
```bash
taskrunner run <file> --parallel
```

## 📁 Project Structure

```
taskrunner/
├── cli.py          # Command-line interface
├── core.py         # Base plugin class
├── plugins/        # Built-in plugins
├── models/         # Data models
├── tasks/          # Task execution logic
└── utils/          # Utility functions
```

## 🧪 Examples

Check the `examples/` directory for comprehensive examples in both YAML and JSON formats.