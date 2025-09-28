from fastapi import Depends, HTTPException, status, FastAPI
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.users.models import UserModel, TokenModel
from app.core.database import get_db
from sqlalchemy.orm import Session


security = HTTPBearer(scheme_name="Token")


def get_current_username(credentials: HTTPAuthorizationCredentials = Depends(security),
                         db: Session = Depends(get_db)):
    token_object = db.query(TokenModel).filter_by(token=credentials.credentials).first()
    if not token_object:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed.",
                            )
    return token_object.user
