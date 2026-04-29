import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


class SchedulerService:
    @staticmethod
    def process_reminders() -> None:
        db = SessionLocal()
        try:
            sent_count = NotificationService.dispatch_pending_notifications(db)
            if sent_count:
                logger.info("Processed %s pending notifications", sent_count)
        finally:
            db.close()

    @staticmethod
    def start() -> None:
        if scheduler.running:
            return

        scheduler.add_job(
            SchedulerService.process_reminders,
            "interval",
            minutes=1,
            id="process-reminders",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Reminder scheduler started")

    @staticmethod
    def shutdown() -> None:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("Reminder scheduler stopped")
