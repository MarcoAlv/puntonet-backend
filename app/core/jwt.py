import jwt
import uuid
from datetime import (
        datetime,
        timezone,
        timedelta,
    )
from app.core.db.redis import redis_client
from app.config.base import (
        PUBLIC_KEY,
        PRIVATE_KEY,
        JWT_ALGORITHM,
        ACCESS_TOKEN_EXPIRE_MINUTES
    )
from app.models.users import User


async def create_token(data: dict, expires_delta: timedelta | None = None):
    now = int(datetime.now(timezone.utc).timestamp())
    dlt = (int(expires_delta.total_seconds())
        if expires_delta
        else ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    exp = now + dlt
    jti = str(uuid.uuid4())

    await redis_client.set(f"wljwt:{jti.replace("-", "")}", "1",ex=dlt)

    payload = {
        **data,
        "iat": now,
        "nbf": now,
        "exp": exp,
        "jti": jti,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if payload["exp"] < now_ts:
            raise ValueError("Token expired")
        if payload.get("nbf", 0) > now_ts:
            raise ValueError("Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
