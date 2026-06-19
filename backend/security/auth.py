import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Callable

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext

from backend.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

# ---- Password hashing ----


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---- JWT ----


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = verify_token(credentials.credentials)
    return {
        "sub": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role", "user"),
        "jti": payload.get("jti"),
    }


def require_role(allowed_roles: list[str]) -> Callable:
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return role_checker


# ---- Rate limiter (token bucket, in-memory) ----


class TokenBucketRateLimiter:
    def __init__(self, rate: int = 10, per_seconds: int = 60):
        self.rate = rate
        self.per_seconds = per_seconds
        self._buckets: dict[str, dict] = {}

    def _get_bucket_key(self, request: Request) -> str:
        client_ip = request.client.host if request.client else "unknown"
        route_path = request.url.path
        return f"{client_ip}:{route_path}"

    async def __call__(self, request: Request):
        key = self._get_bucket_key(request)
        now = time.monotonic()
        bucket = self._buckets.get(key)

        if bucket is None:
            bucket = {"tokens": self.rate, "last_refill": now}
            self._buckets[key] = bucket

        elapsed = now - bucket["last_refill"]
        refill = elapsed * (self.rate / self.per_seconds)
        bucket["tokens"] = min(self.rate, bucket["tokens"] + refill)
        bucket["last_refill"] = now

        if bucket["tokens"] < 1:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        bucket["tokens"] -= 1


rate_limiter = TokenBucketRateLimiter(rate=60, per_seconds=60)
