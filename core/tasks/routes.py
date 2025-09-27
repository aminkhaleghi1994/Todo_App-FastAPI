from fastapi import APIRouter, Path, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from tasks.schemas import *
from tasks.models import TaskModel
from users.models import UserModel
from sqlalchemy.orm import Session
from core.database import get_db
from typing import List
from auth.jwt_auth import get_authenticated_user


router = APIRouter(tags=["tasks"], prefix="/todos")


@router.get("/tasks", response_model=List[TaskResponseSchema])
async def retrieve_tasks(
        completed: bool = Query(None, description="filter tasks based on being completed or not"),
        limit: int = Query(10, gt=0, le=50, description="limiting the number of items to retrieve"),
        offset: int = Query(0, ge=0, description="use for paginating based on passed items"),
        db: Session = Depends(get_db),
        user: UserModel = Depends(get_authenticated_user)):
    query = db.query(TaskModel).filter_by(user_id=user.id)
    if completed is not None:
        query = query.filter_by(is_completed=completed)

    return query.offset(offset).limit(limit).all()


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def retrieve_tasks_detail(task_id: int = Path(..., gt=0),
                                db: Session = Depends(get_db),
                                user: UserModel = Depends(get_authenticated_user)):
    task_object = db.query(TaskModel).filter_by(user_id = user.id, id=task_id).first()
    if not task_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_object


@router.post("/tasks", response_model=TaskResponseSchema)
async def create_task(request: TaskCreateSchema,
                      db: Session = Depends(get_db),
                      user: UserModel = Depends(get_authenticated_user)):

    user = db.query(UserModel).filter_by(id=user.id).first()
    if user:
        data = request.model_dump()
        data.update({"user_id": user.id})
        task_object = TaskModel()
        db.add(task_object)
        db.commit()
        db.refresh(task_object)
        return task_object
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not authorized to perform this action")

@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(request: TaskUpdateSchema,
                      task_id: int = Path(..., gt=0),
                      db: Session = Depends(get_db)):
    task_object = db.query(TaskModel).filter_by(id=task_id).first()
    if not task_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(task_object, field, value)

    db.commit()
    db.refresh(task_object)
    return task_object


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int = Path(..., gt=0),
                      db: Session = Depends(get_db),
                      user: UserModel = Depends(get_authenticated_user)):
    task_object = db.query(TaskModel).filter_by(user_id=user.id, id=task_id).first()
    if not task_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task_object)
    db.commit()
