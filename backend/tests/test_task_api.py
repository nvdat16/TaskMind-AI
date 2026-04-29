from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.api import deps
from app.api.v1 import tasks as tasks_api
from app.main import app


def _fake_task(**overrides):
    now = datetime.now(timezone.utc)
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "title": "Prepare slides",
        "description": "10 slides for meeting",
        "category": "work",
        "priority": "high",
        "status": "todo",
        "due_at": None,
        "estimated_minutes": 60,
        "reminder_at": None,
        "source_type": "manual",
        "ai_metadata": None,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_create_task_returns_created_task(client, monkeypatch) -> None:
    current_user = SimpleNamespace(id=uuid4())
    task = _fake_task(user_id=current_user.id)

    app.dependency_overrides[deps.get_current_user] = lambda: current_user
    monkeypatch.setattr(tasks_api.TaskService, "create_task", lambda db, user_id, payload: task)

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Prepare slides",
            "description": "10 slides for meeting",
            "category": "work",
            "priority": "high",
            "status": "todo",
            "estimated_minutes": 60,
            "source_type": "manual",
            "ai_metadata": None,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Prepare slides"
    assert body["priority"] == "high"


def test_list_tasks_returns_items(client, monkeypatch) -> None:
    current_user = SimpleNamespace(id=uuid4())
    tasks = [_fake_task(user_id=current_user.id), _fake_task(user_id=current_user.id, title="Call mom")]

    app.dependency_overrides[deps.get_current_user] = lambda: current_user
    monkeypatch.setattr(tasks_api.TaskService, "list_tasks", lambda db, user_id: tasks)

    response = client.get("/api/v1/tasks")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_update_task_returns_updated_task(client, monkeypatch) -> None:
    current_user = SimpleNamespace(id=uuid4())
    task = _fake_task(user_id=current_user.id, status="doing")

    app.dependency_overrides[deps.get_current_user] = lambda: current_user
    monkeypatch.setattr(tasks_api.TaskService, "update_task", lambda db, user_id, task_id, payload: task)

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"status": "doing"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "doing"


def test_delete_task_returns_message(client, monkeypatch) -> None:
    current_user = SimpleNamespace(id=uuid4())

    app.dependency_overrides[deps.get_current_user] = lambda: current_user
    monkeypatch.setattr(tasks_api.TaskService, "delete_task", lambda db, user_id, task_id: None)

    response = client.delete(f"/api/v1/tasks/{uuid4()}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted successfully"}
