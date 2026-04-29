import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def create_notification(
        db: Session, user_id: UUID, payload: NotificationCreate
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            task_id=payload.task_id,
            channel=payload.channel,
            notification_type=payload.notification_type,
            scheduled_at=payload.scheduled_at,
            sent_at=payload.sent_at,
            status=payload.status,
            payload=payload.payload,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_pending_notifications(db: Session) -> list[Notification]:
        now = datetime.now(UTC)
        return (
            db.query(Notification)
            .filter(
                Notification.status == "pending",
                Notification.scheduled_at <= now,
            )
            .order_by(Notification.scheduled_at.asc())
            .all()
        )

    @staticmethod
    def mark_as_sent(db: Session, notification: Notification) -> Notification:
        notification.status = "sent"
        notification.sent_at = datetime.now(UTC)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def dispatch_pending_notifications(db: Session) -> int:
        notifications = NotificationService.get_pending_notifications(db)
        for notification in notifications:
            logger.info(
                "Dispatching notification id=%s type=%s channel=%s",
                notification.id,
                notification.notification_type,
                notification.channel,
            )
            NotificationService.mark_as_sent(db, notification)
        return len(notifications)
