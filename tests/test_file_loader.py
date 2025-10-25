import pytest
import json
import yaml
import tempfile
import os
from taskrunner.utils.file_loader import load_tasks_from_file, FileLoaderMessages
from taskrunner.models.task_model import TaskModel


def test_load_tasks_from_json_file():
    # Create temporary JSON file with test data
    test_tasks = [
        {"name": "task1", "type": "log", "config": {"message": "Hello"}},
        {"name": "task2", "type": "wait", "config": {"seconds": 1}}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_tasks, f)
        temp_file_path = f.name
    
    try:
        tasks = load_tasks_from_file(temp_file_path)
        
        assert len(tasks) == 2
        assert isinstance(tasks[0], TaskModel)
        assert tasks[0].name == "task1"
        assert tasks[0].type == "log"
        assert tasks[0].config == {"message": "Hello"}
        
        assert isinstance(tasks[1], TaskModel)
        assert tasks[1].name == "task2"
        assert tasks[1].type == "wait"
        assert tasks[1].config == {"seconds": 1}
    finally:
        os.unlink(temp_file_path)


def test_load_tasks_from_yaml_file():
    # Create temporary YAML file with test data
    test_tasks = [
        {"name": "task1", "type": "log", "config": {"message": "Hello"}},
        {"name": "task2", "type": "wait", "config": {"seconds": 1}}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(test_tasks, f)
        temp_file_path = f.name
    
    try:
        tasks = load_tasks_from_file(temp_file_path)
        
        assert len(tasks) == 2
        assert isinstance(tasks[0], TaskModel)
        assert tasks[0].name == "task1"
        assert tasks[0].type == "log"
        assert tasks[0].config == {"message": "Hello"}
    finally:
        os.unlink(temp_file_path)


def test_load_tasks_from_yml_file():
    # Create temporary YML file with test data
    test_tasks = [
        {"name": "task1", "type": "log", "config": {"message": "Hello"}}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(test_tasks, f)
        temp_file_path = f.name
    
    try:
        tasks = load_tasks_from_file(temp_file_path)
        
        assert len(tasks) == 1
        assert isinstance(tasks[0], TaskModel)
        assert tasks[0].name == "task1"
        assert tasks[0].type == "log"
    finally:
        os.unlink(temp_file_path)


def test_load_tasks_file_not_found():
    with pytest.raises(FileNotFoundError) as exc_info:
        load_tasks_from_file("non_existent_file.json")
    
    assert FileLoaderMessages.FILE_NOT_FOUND.value.format("non_existent_file.json") in str(exc_info.value)


def test_load_tasks_unsupported_format():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content")
        temp_file_path = f.name
    
    try:
        with pytest.raises(ValueError) as exc_info:
            load_tasks_from_file(temp_file_path)
        
        assert FileLoaderMessages.UNSUPPORTED_FORMAT.value in str(exc_info.value)
    finally:
        os.unlink(temp_file_path)


def test_load_tasks_invalid_format():
    # Create JSON file with invalid format (not a list)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"name": "invalid"}, f)
        temp_file_path = f.name
    
    try:
        with pytest.raises(ValueError) as exc_info:
            load_tasks_from_file(temp_file_path)
        
        assert FileLoaderMessages.INVALID_TASKS_FORMAT.value in str(exc_info.value)
    finally:
        os.unlink(temp_file_path)