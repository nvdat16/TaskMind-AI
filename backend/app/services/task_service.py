from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.task_log import TaskLog
from app.models.user import User
from app.schemas.notification import NotificationCreate
from app.schemas.task import TaskCreate
from app.schemas.task import TaskUpdate
from app.services.notification_service import NotificationService


class TaskService:
    @staticmethod
    def create_task(db: Session, user_id: UUID, payload: TaskCreate) -> Task:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if payload.due_at and payload.reminder_at and payload.reminder_at > payload.due_at:
            raise ValueError("reminder_at cannot be later than due_at")

        task = Task(
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            category=payload.category,
            priority=payload.priority,
            status=payload.status,
            due_at=payload.due_at,
            estimated_minutes=payload.estimated_minutes,
            reminder_at=payload.reminder_at,
            source_type=payload.source_type,
            ai_metadata=payload.ai_metadata,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        TaskService._log_task_action(
            db=db,
            task_id=task.id,
            action_type="created",
            new_value={
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
            },
        )

        if task.reminder_at:
            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                payload=NotificationCreate(
                    task_id=task.id,
                    notification_type="reminder",
                    scheduled_at=task.reminder_at,
                    payload={"task_title": task.title},
                ),
            )
        return task

    @staticmethod
    def list_tasks(db: Session, user_id: UUID) -> list[Task]:
        return (
            db.query(Task)
            .filter(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
            .all()
        )

    @staticmethod
    def get_task(db: Session, user_id: UUID, task_id: UUID) -> Task:
        task = (
            db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user_id)
            .first()
        )
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    @staticmethod
    def update_task(db: Session, user_id: UUID, task_id: UUID, payload: TaskUpdate) -> Task:
        task = TaskService.get_task(db, user_id, task_id)
        if payload.due_at and payload.reminder_at and payload.reminder_at > payload.due_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="reminder_at cannot be later than due_at",
            )

        old_value = {
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
            "due_at": task.due_at.isoformat() if task.due_at else None,
            "reminder_at": task.reminder_at.isoformat() if task.reminder_at else None,
        }

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        db.add(task)
        db.commit()
        db.refresh(task)

        TaskService._log_task_action(
            db=db,
            task_id=task.id,
            action_type="updated",
            old_value=old_value,
            new_value=update_data,
        )
        return task

    @staticmethod
    def delete_task(db: Session, user_id: UUID, task_id: UUID) -> None:
        task = TaskService.get_task(db, user_id, task_id)
        TaskService._log_task_action(
            db=db,
            task_id=task.id,
            action_type="deleted",
            old_value={
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
            },
        )
        db.delete(task)
        db.commit()

    @staticmethod
    def _log_task_action(
        db: Session,
        task_id: object,
        action_type: str,
        old_value: dict | None = None,
        new_value: dict | None = None,
    ) -> None:
        log = TaskLog(
            task_id=task_id,
            action_type=action_type,
            old_value=old_value,
            new_value=new_value,
        )
        db.add(log)
        db.commit()
