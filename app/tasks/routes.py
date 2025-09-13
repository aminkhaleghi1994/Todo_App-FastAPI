from fastapi import APIRouter

router = APIRouter(tags=["tasks"], prefix="/todos")


@router.get("/tasks")
async def retrieve_tasks():
    return []


@router.get("/tasks/{task_id}")
async def retrieve_tasks_detail(task_id: int):
    return []
