from taskrunner.core import BaseTaskRunner


class ExternalTask(BaseTaskRunner):
    type_name = "external"

    def run(self, config):
        message = config.get("message", "This is an external plugin!")
        print(f"[ExternalTask] {message}")
