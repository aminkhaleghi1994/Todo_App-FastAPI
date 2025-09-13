from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class UserLoginSchema(BaseModel):
    username: str = Field(..., max_length=250, description="Username of the user")
    password: str = Field(..., description="Password of the user")


class UserRegisterSchema(BaseModel):
    username: str = Field(..., max_length=250, description="Username of the user")
    password: str = Field(..., description="Password of the user")
    password_confirmation: str = Field(..., description="Confirm password of the user")

    @field_validator("password_confirmation")
    def check_password_match(cls, password_confirmation, validation):
        if not (password_confirmation == validation.data.get('password')):
            raise ValueError("Password does not match")
        return password_confirmation