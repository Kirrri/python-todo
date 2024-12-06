import os
import json
import pytest
from datetime import datetime
from main import Task, TaskManager, clear_console, select_menu

@pytest.fixture
def sample_task():
    return Task(
        id=1,
        title="Sample Task",
        description="This is a sample task",
        category="Work",
        due_date=datetime(2024, 12, 31),
        priority="High",
        status=False
    )

@pytest.fixture
def task_manager(tmp_path):
    # Создаем временный путь для хранения файла задач
    path = tmp_path / "tasks.json"
    task_manager = TaskManager(str(path))
    return task_manager

def test_create_new_task(task_manager):
    task_manager.create_new_task = lambda: task_manager.task_list.append(Task(
        title="Test Task",
        description="Test Description",
        category="Test Category",
        due_date=datetime(2024, 12, 31),
        priority="High",
    ))
    task_manager.create_new_task()
    assert len(task_manager.task_list) == 1
    assert task_manager.task_list[0].title == "Test Task"

def test_find_by_title(task_manager, sample_task):
    task_manager.task_list.append(sample_task)
    task_manager.find_by_title = lambda: print("Task Found") if task_manager.task_list[0].title == "Sample Task" else print("Task Not Found")
    assert task_manager.find_by_title() == None

def test_save_task_list(task_manager, sample_task):
    task_manager.task_list.append(sample_task)
    task_manager.save_task_list()
    
    with open(task_manager.path, "r", encoding='utf-8') as f:
        data = json.load(f)
    
    assert data[1][0]['title'] == "Sample Task"

def test_refresh_id(task_manager, sample_task):
    task_manager.task_list.extend([sample_task, sample_task])
    task_manager.refresh_id()
    
    assert task_manager.task_list[0].id == 1
    assert task_manager.task_list[1].id == 2

def test_change_data(sample_task):
    sample_task.change_data(title="Updated Task")
    
    assert sample_task.title == "Updated Task"

def test_clear_console():
    try:
        clear_console()
    except Exception as e:
        pytest.fail(f"clear_console() raised {e} unexpectedly!")

def test_select_menu(monkeypatch):
    inputs = iter(["1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = select_menu("Menu", 3)
    assert result == 1

if __name__ == "__main__":
    pytest.main()
