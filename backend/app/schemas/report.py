from datetime import date, datetime
from uuid import UUID

from app.schemas.common import AppBaseSchema


class DailyReportResponse(AppBaseSchema):
    id: UUID
    user_id: UUID
    report_date: date
    summary_text: str
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    productivity_score: int | None = None
    created_at: datetime
