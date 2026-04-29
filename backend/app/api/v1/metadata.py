from fastapi import APIRouter

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("/task-options")
def get_task_options() -> dict[str, list[str]]:
    return {
        "categories": ["general", "work", "personal", "health", "study", "finance"],
        "priorities": ["low", "medium", "high", "urgent"],
        "statuses": ["todo", "doing", "done", "snoozed", "cancelled"],
    }
