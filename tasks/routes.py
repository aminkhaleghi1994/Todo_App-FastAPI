from fastapi import APIRouter, Path, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from tasks.schemas import *
from tasks.models import TaskModel
from sqlalchemy.orm import Session
from core.database import get_db
from typing import List


router = APIRouter(tags=["tasks"], prefix="/todos")


@router.get("/tasks", response_model=List[TaskResponseSchema])
async def retrieve_tasks(
        completed: bool = Query(None, description="filter tasks based on being completed or not"),
        limit: bool = Query(10, gt=0, le=50, description="limiting the number of items to retrieve"),
        offset: bool = Query(0, ge=0, description="use for paginating based on passed items"),
        db: Session = Depends(get_db)):
    query = db.query(TaskModel)
    if completed is not None:
        query = query.filter_by(is_completed=completed)

    return query.offset(offset).limit(limit).all()


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def retrieve_tasks_detail(task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task_object = db.query(TaskModel).filter_by(id=task_id).first()
    if not task_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_object


@router.post("/tasks", response_model=TaskResponseSchema)
async def create_task(request: TaskCreateSchema, db: Session = Depends(get_db)):
    task_object = TaskModel(**request.model_dump())
    db.add(task_object)
    db.commit()
    db.refresh(task_object)
    return task_object


@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(request: TaskUpdateSchema, task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task_object = db.query(TaskModel).filter_by(id=task_id).first()
    if not task_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(task_object, field, value)

    db.commit()
    db.refresh(task_object)
    return task_object


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task_object = db.query(TaskModel).filter_by(id=task_id).first()
    if not task_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task_object)
    db.commit()
