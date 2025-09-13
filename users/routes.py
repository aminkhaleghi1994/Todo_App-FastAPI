from fastapi import APIRouter, Path, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from users.schemas import *
from users.models import UserModel
from sqlalchemy.orm import Session
from core.database import get_db
from typing import List


router = APIRouter(tags=["users"], prefix="/users")


@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user_object = db.query(UserModel).filter(username == request.username.lower()).first()
    if not user_object:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
    if not user_object.verify_password(request.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is invalid")
    return {}


@router.post("/register")
async def user_login(request: UserRegisterSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter_by(username == request.username.lower()).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user_object = UserModel(username=request.username.lower())
    user_object.set_password(request.password)
    db.add(user_object)
    db.commit()
    db.refresh(user_object)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content="user object successfully registered")
