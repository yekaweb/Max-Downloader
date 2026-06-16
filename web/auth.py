"""JWT authentication for web admin panel"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer security
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_admin(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """
    Validate JWT token and return admin info.
    Used as a dependency for protected routes.
    """
    token = credentials.credentials

    try:
        payload = verify_token(token)

        user_id: int = payload.get("user_id")
        is_admin: bool = payload.get("is_admin", False)

        if user_id is None or not is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")

        return {"user_id": user_id, "is_admin": is_admin}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_token",
    "get_current_admin",
]
