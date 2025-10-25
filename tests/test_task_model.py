import pytest
from taskrunner.models.task_model import TaskModel


def test_task_model_creation():
    task_data = {
        "name": "test_task",
        "type": "log",
        "config": {"message": "Hello, World!"}
    }
    
    task = TaskModel(**task_data)
    
    assert task.name == "test_task"
    assert task.type == "log"
    assert task.config == {"message": "Hello, World!"}


def test_task_model_default_config():
    task_data = {
        "name": "test_task",
        "type": "log"
    }
    
    task = TaskModel(**task_data)
    
    assert task.name == "test_task"
    assert task.type == "log"
    assert task.config == {}


def test_task_model_invalid_data():
    # Missing name
    with pytest.raises(Exception):
        TaskModel(type="log", config={"message": "Hello"})
    
    # Missing type
    with pytest.raises(Exception):
        TaskModel(name="test_task", config={"message": "Hello"})