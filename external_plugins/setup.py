from setuptools import setup, find_packages

setup(
    name="taskrunner-external-example",
    version="0.1.0",
    description="Example external plugin for TaskRunner",
    packages=find_packages(),
    install_requires=[
        "taskrunner",
    ],
    entry_points={
        # This is just an example - in a real scenario, you might have entry points
    },
)