# 🧩 TaskRunner – Plugin-Based Task Runner in Python

TaskRunner is a lightweight, extensible command-line tool that executes tasks defined in JSON or YAML files.
It’s built around a plugin architecture — drop in new task types without touching the core code.

---

## 🚀 Features

* **Plugin architecture** – Add new task types by subclassing `BaseTaskRunner`.
* **Strict validation** – Uses Pydantic to ensure tasks are well-formed.
* **Dynamic discovery** – Automatically finds plugins from the `plugins/` folder.
* **CLI interface** – Powered by Click with commands for running, validating, and listing tasks.
* **Built-in plugins**:

  * `LogTask` – Prints a message
  * `WaitTask` – Delays execution
  * `HttpGetTask` – Sends a GET request and prints the status code

---

## 🧱 Example Task File

```yaml
- name: greet
  type: log
  config:
    message: "Hello, world!"

- name: pause
  type: wait
  config:
    seconds: 2

- name: check_site
  type: http_get
  config:
    url: "https://example.com"
```

---

## 🕹️ Usage

```bash
# Validate a task file
taskrunner validate tasks.yaml

# Run all tasks
taskrunner run tasks.yaml

# Run only one task by name
taskrunner run tasks.yaml --only greet

# List all available plugins
taskrunner list-plugins
```

---

## 🧩 Adding New Plugins

Create a new file under `taskrunner/plugins/` and subclass `BaseTaskRunner`:

```python
from taskrunner.core import BaseTaskRunner

class MyTask(BaseTaskRunner):
    type_name = "my_task"

    def run(self, config):
        print("Running my custom task:", config)
```

That’s it — your new plugin is instantly discoverable.

---

## ⚙️ Installation

```bash
pip install -e .
```

After installation, the CLI command `taskrunner` becomes available globally.
