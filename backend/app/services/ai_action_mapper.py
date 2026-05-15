from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.schemas.chat import ChatResponse, ParsedTaskData
from app.schemas.task import TaskCreate
from app.services.task_service import TaskService

logger = logging.getLogger(__name__)

PRIORITY_SCORE = {
    "urgent": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


@dataclass(slots=True)
class AIActionResult:
    response: ChatResponse
    action_name: str
    task: Task | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AIActionMapper:
    @staticmethod
    def _build_create_task_payload(parsed_task: ParsedTaskData) -> TaskCreate:
        if not parsed_task.title:
            raise ValueError("parsed_task.title is required")

        return TaskCreate(
            title=parsed_task.title.strip(),
            description=parsed_task.description,
            category=parsed_task.category or "general",
            priority=parsed_task.priority or "medium",
            status="todo",
            due_at=parsed_task.due_at,
            reminder_at=parsed_task.reminder_at,
            source_type="ai_chat",
            ai_metadata={
                "origin": "chat",
                "parsed_task": parsed_task.model_dump(mode="json"),
            },
        )

    @staticmethod
    def _normalize_datetime(value: datetime | None) -> datetime:
        if value is None:
            return datetime.max.replace(tzinfo=UTC)
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value

    @classmethod
    def _sort_key(cls, task: Task) -> tuple[int, datetime, datetime]:
        priority_score = PRIORITY_SCORE.get(task.priority, 2)
        due_at = cls._normalize_datetime(task.due_at)
        created_at = cls._normalize_datetime(task.created_at)
        return (-priority_score, due_at, created_at)

    @classmethod
    def _top_tasks(cls, tasks: list[Task], limit: int = 3) -> list[Task]:
        return sorted(tasks, key=cls._sort_key)[:limit]

    @staticmethod
    def _format_task_lines(tasks: list[Task]) -> str:
        if not tasks:
            return "Chưa có task nào."

        lines: list[str] = []
        for index, task in enumerate(tasks, start=1):
            deadline = task.due_at.isoformat() if task.due_at else "không có deadline"
            lines.append(
                f"{index}. {task.title} | ưu tiên {task.priority} | trạng thái {task.status} | {deadline}"
            )
        return "\n".join(lines)

    @classmethod
    def execute(
        cls,
        db: Session,
        user: User,
        response: ChatResponse,
    ) -> AIActionResult:
        logger.info(
            "AI decision intent=%s needs_confirmation=%s user_id=%s",
            response.intent,
            response.needs_confirmation,
            user.id,
        )

        if response.intent == "create_task":
            return cls._execute_create_task(db=db, user=user, response=response)
        if response.intent == "list_tasks":
            return cls._execute_list_tasks(db=db, user=user, response=response)
        if response.intent == "plan_today":
            return cls._execute_plan_today(db=db, user=user, response=response)
        if response.intent == "daily_summary":
            return cls._execute_daily_summary(db=db, user=user, response=response)

        fallback = ChatResponse(
            reply="Mình chưa hiểu rõ yêu cầu. Bạn có thể nói lại ngắn gọn hơn không?",
            intent="unknown",
            needs_confirmation=False,
            missing_fields=[],
            parsed_task=response.parsed_task,
        )
        return AIActionResult(response=fallback, action_name="unknown")

    @classmethod
    def _execute_create_task(
        cls,
        db: Session,
        user: User,
        response: ChatResponse,
    ) -> AIActionResult:
        if response.needs_confirmation:
            reply = response.reply or "Mình cần bạn xác nhận thêm trước khi tạo task này."
            return AIActionResult(
                response=ChatResponse(
                    reply=reply,
                    intent="create_task",
                    needs_confirmation=True,
                    missing_fields=response.missing_fields,
                    parsed_task=response.parsed_task,
                ),
                action_name="create_task_pending_confirmation",
                metadata={"missing_fields": response.missing_fields},
            )

        if response.parsed_task is None:
            return AIActionResult(
                response=ChatResponse(
                    reply="Mình chưa tách được task từ tin nhắn này.",
                    intent="unknown",
                    needs_confirmation=False,
                    missing_fields=[],
                    parsed_task=None,
                ),
                action_name="create_task_failed",
            )

        payload = cls._build_create_task_payload(response.parsed_task)
        task = TaskService.create_task(db, user.id, payload)
        reply = f'Đã tạo task "{task.title}".'
        result = ChatResponse(
            reply=reply,
            intent="create_task",
            needs_confirmation=False,
            missing_fields=[],
            parsed_task=response.parsed_task,
        )
        return AIActionResult(
            response=result,
            action_name="create_task",
            task=task,
            metadata={"task_id": str(task.id), "title": task.title},
        )

    @classmethod
    def _execute_list_tasks(
        cls,
        db: Session,
        user: User,
        response: ChatResponse,
    ) -> AIActionResult:
        tasks = TaskService.list_tasks(db, user.id)
        reply = "Danh sách task hiện tại:\n" + cls._format_task_lines(tasks[:5])
        return AIActionResult(
            response=ChatResponse(
                reply=reply,
                intent="list_tasks",
                needs_confirmation=False,
                missing_fields=[],
                parsed_task=None,
            ),
            action_name="list_tasks",
            metadata={"total": len(tasks)},
        )

    @classmethod
    def _execute_plan_today(
        cls,
        db: Session,
        user: User,
        response: ChatResponse,
    ) -> AIActionResult:
        tasks = TaskService.list_tasks(db, user.id)
        top_tasks = cls._top_tasks(tasks)
        if not top_tasks:
            reply = "Hôm nay bạn chưa có task nào."
        else:
            reply = "3 việc nên làm hôm nay:\n" + cls._format_task_lines(top_tasks)
        return AIActionResult(
            response=ChatResponse(
                reply=reply,
                intent="plan_today",
                needs_confirmation=False,
                missing_fields=[],
                parsed_task=None,
            ),
            action_name="plan_today",
            metadata={"top_task_count": len(top_tasks)},
        )

    @classmethod
    def _execute_daily_summary(
        cls,
        db: Session,
        user: User,
        response: ChatResponse,
    ) -> AIActionResult:
        tasks = TaskService.list_tasks(db, user.id)
        done_count = sum(1 for task in tasks if task.status == "done")
        pending_count = sum(1 for task in tasks if task.status in {"todo", "doing", "snoozed"})
        reply = (
            f"Tổng kết nhanh: đã hoàn thành {done_count} task, còn {pending_count} task đang mở."
        )
        return AIActionResult(
            response=ChatResponse(
                reply=reply,
                intent="daily_summary",
                needs_confirmation=False,
                missing_fields=[],
                parsed_task=None,
            ),
            action_name="daily_summary",
            metadata={"done_count": done_count, "pending_count": pending_count},
        )
