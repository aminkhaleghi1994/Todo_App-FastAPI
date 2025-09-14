from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from users.models import UserModel
from core.database import get_db
from sqlalchemy.orm import Session


security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security),
                         db: Session = Depends(get_db)):
    user_object = db.query(UserModel).filter_by(username=credentials.username).first()
    if not user_object:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Basic"},
                            )
    if not user_object.verify_password(credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Basic"},
                            )
    return user_object