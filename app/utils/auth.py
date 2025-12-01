from datetime import timedelta
from typing import Tuple
from app.models.users import User
from app.core.jwt import create_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.jwt import decode_jwt_token
from sqlalchemy import select
from app.core.db.redis import redis_client


async def create_tokens(user: User) -> Tuple[str, str]:
    """
    Args:
        user: the user to generate the tokens for
    Return:
        data: Tuple[str, str] = (access, refresh)
    """
    role = user.role.value
    access = {"sub": str(user.uuid), "type": "access", "role": role}
    refresh = {
        "sub": str(user.uuid),
        "type": "refresh",
        "role": role
    }
    return (
        await create_token(data=access),
        await create_token(data=refresh, expires_delta=timedelta(days=1))
    )


async def claim_token(
    db: AsyncSession,
    token: str,
    token_type: str = "access"
) -> User:
    payload = decode_jwt_token(token)

    if payload.get("type") != token_type:
        raise ValueError(f"Not {token_type} Token")
    
    if payload.get("type") == "refresh":
        is_deleted = await redis_client.delete(
            f"wljwt:{str(payload.get("jti") or "").replace("-", "")}"
        )
        if is_deleted == 0:
            raise ValueError(f"Refresh Token has been already used")
    
    uuid = payload.get("sub")
    stmt = select(User).where(User.uuid == uuid)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError("User not found")
    
    return user
