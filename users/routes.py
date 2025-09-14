from fastapi import APIRouter, Path, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from users.schemas import *
from users.models import UserModel, TokenModel
from sqlalchemy.orm import Session
from core.database import get_db
from typing import List
import secrets


router = APIRouter(tags=["users"], prefix="/users")


def generate_token(length = 32):
    return secrets.token_hex(length)


@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user_object = db.query(UserModel).filter_by(username=request.username.lower()).first()
    if not user_object:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
    if not user_object.verify_password(request.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is invalid")
    token_object = TokenModel(user_id=user_object.id, token=generate_token())
    db.add(token_object)
    db.commit()
    db.refresh(token_object)
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"detail": "user object successfully login",
                                 "token": token_object.token})


@router.post("/register")
async def user_register(request: UserRegisterSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter_by(username=request.username.lower()).one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user_object = UserModel(username=request.username.lower())
    user_object.set_password(request.password)
    db.add(user_object)
    db.commit()
    db.refresh(user_object)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content="user object successfully registered")
