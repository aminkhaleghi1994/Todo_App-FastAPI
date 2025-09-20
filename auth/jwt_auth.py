from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from users.models import UserModel, TokenModel
from core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError
from core.config import settings


security = HTTPBearer()


def get_authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                         db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms="HS256")
        user_id = decoded.get("id", None)
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authentication failed, user_id not found in the payload.")
        if decoded.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authentication failed, wrong token authentication type.")
        if datetime.now() > datetime.fromtimestamp(decoded.get("exp")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authentication failed, token expired.")

        user_object = db.query(UserModel).filter_by(id=user_id).first()
        return user_object
    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed, Invalid Signature.")
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed, decode failed.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Authentication failed, {e} as error.")


def generate_access_token(id: int,
                          expires_in: int = 5*60) -> str:
    now = datetime.utcnow()
    payload = {
        "type": "access",
        "id": id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in)
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def generate_refresh_token(id: int,
                          expires_in: int = 5*3600) -> str:
    now = datetime.utcnow()
    payload = {
        "type": "refresh",
        "id": id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in)
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def decode_refresh_token(token: str,
                         db: Session = Depends(get_db)):
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms="HS256")
        user_id = decoded.get("id", None)
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authentication failed, user_id not found in the payload.")
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authentication failed, wrong token authentication type.")
        if datetime.now() > datetime.fromtimestamp(decoded.get("exp")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Authentication failed, token expired.")
        return user_id

    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed, Invalid Signature.")
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed, decode failed.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Authentication failed, {e} as error.")