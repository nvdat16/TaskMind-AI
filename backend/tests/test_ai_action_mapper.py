from types import SimpleNamespace
from uuid import uuid4

from app.schemas.chat import ChatResponse, ParsedTaskData
from app.services.ai_action_mapper import AIActionMapper


def test_execute_create_task(monkeypatch) -> None:
    created_payload = {}

    def fake_create_task(db, user_id, payload):
        created_payload["user_id"] = user_id
        created_payload["payload"] = payload
        return SimpleNamespace(id=uuid4(), title=payload.title)

    monkeypatch.setattr("app.services.ai_action_mapper.TaskService.create_task", fake_create_task)

    user = SimpleNamespace(id=uuid4())
    response = ChatResponse(
        reply="Đã hiểu yêu cầu của bạn.",
        intent="create_task",
        needs_confirmation=False,
        missing_fields=[],
        parsed_task=ParsedTaskData(
            title="Chuẩn bị slide",
            description="Cho cuộc họp sáng mai",
            category="work",
            priority="high",
            due_at=None,
            reminder_at=None,
        ),
    )

    result = AIActionMapper.execute(db=SimpleNamespace(), user=user, response=response)

    assert result.action_name == "create_task"
    assert created_payload["user_id"] == user.id
    assert created_payload["payload"].title == "Chuẩn bị slide"
    assert result.response.intent == "create_task"


def test_execute_plan_today(monkeypatch) -> None:
    tasks = [
        SimpleNamespace(
            title="Task A",
            priority="urgent",
            status="todo",
            due_at=None,
            created_at=None,
        ),
        SimpleNamespace(
            title="Task B",
            priority="low",
            status="todo",
            due_at=None,
            created_at=None,
        ),
    ]

    monkeypatch.setattr("app.services.ai_action_mapper.TaskService.list_tasks", lambda db, user_id: tasks)

    user = SimpleNamespace(id=uuid4())
    response = ChatResponse(reply="x", intent="plan_today")

    result = AIActionMapper.execute(db=SimpleNamespace(), user=user, response=response)

    assert result.action_name == "plan_today"
    assert "3 việc nên làm hôm nay" in result.response.reply
