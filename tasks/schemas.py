from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskBaseSchema(BaseModel):
    title: str = Field(..., max_length=150, min_length=5, description='title of the task')
    description: Optional[str] = Field(None, max_length=500, description='description of the task')
    is_completed: bool = Field(..., description='state of the task')


class TaskCreateSchema(TaskBaseSchema):
    pass


class TaskUpdateSchema(TaskBaseSchema):
    pass


class TaskResponseSchema(TaskBaseSchema):
    id: int = Field(..., description='Unique identifier of the object')

    created_date: datetime = Field(..., description='creation date and time of the object')
    updated_date: datetime = Field(..., description='updating date and time of the object')