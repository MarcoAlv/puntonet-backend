from typing import Annotated, Callable, List, Optional
from fastapi import HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User
from fastapi import Request, Depends
from app.utils.auth import claim_token
from app.core.db.sessionmanager import get_session


async def auth_dependency(
    request: Request,
    Authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_session)
) -> Optional[User]:
    if Authorization is None:
        raise HTTPException(
            status_code=400,
            detail="Authorization header missing"
        )

    auth_header = Authorization
    if auth_header is None:
        request.state.user = None
        request.state.db = db
        return

    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token.")

    token = auth_header[7:]
    try:
        user = await claim_token(db=db, token=token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    request.state.user = user
    request.state.db = db
    
    return user


def basic_permission_dependency(
    allowed_roles: List[User.BaseUserRole]
) -> Callable:
    async def m(
        request: Request,
        dependency_user = Depends(auth_dependency)
    ) -> User:
        user = getattr(request.state, "user", None)

        if not isinstance(user, User) or user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")

        if user.role not in allowed_roles and len(allowed_roles) != 0:
            raise HTTPException(status_code=401, detail="Not allowed")
        
        return user

    return m
