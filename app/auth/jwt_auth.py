from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.users.models import UserModel, TokenModel
from app.core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidSignatureError, DecodeError, ExpiredSignatureError
from app.core.config import settings


security = HTTPBearer(auto_error=False)


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # 1) Missing/malformed credentials -> 401 with WWW-Authenticate: Bearer
    if credentials is None or (credentials.scheme or "").lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: missing or invalid Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        # 2) Decode & verify JWT (verifies exp/signature by default)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

        # 3) Validate claims & type
        user_id = decoded.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: user_id missing in token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if decoded.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: wrong token type.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 4) Load user
        user_object = db.query(UserModel).filter_by(id=user_id).first()
        # Token points to no user -> treat as invalid credentials -> 401
        if user_object is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: user not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # User exists but is not allowed (e.g., inactive/banned) -> 403
        if hasattr(user_object, "is_active") and not user_object.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: user is inactive.",
            )

        return user_object

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: invalid signature.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: token decode error.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        # re-raise structured HTTP errors
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e}.",
            headers={"WWW-Authenticate": "Bearer"},
        )



def generate_access_token(id: int,
                          expires_in: int = 5*60) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "type": "access",
        "id": id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in)
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def generate_refresh_token(id: int,
                          expires_in: int = 5*3600) -> str:
    now = datetime.now(timezone.utc)
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