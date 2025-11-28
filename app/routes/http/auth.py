"""
Collection of all the
``` HTTP
/api/v{x}/auth
```
routes
"""
import uuid
from sqlalchemy import select
from app.models.users import User
from app.managers.users import Users
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.sessionmanager import get_session
from app.utils.auth import create_tokens, claim_token
from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.encryption import hash_password, verify_password
from app.schemas.users import JWTRefresh, UserLogin, UserRegister, JWTResponse


auth_routes = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@auth_routes.post("/register", response_model=JWTResponse)
async def register_user(
    data: UserRegister,
    db: AsyncSession = Depends(get_session)
):
    res = await db.execute(select(User).where(
        (User.email == data.email)
    ))
    user = res.scalar_one_or_none()
    if user and user.email == data.email:
        raise HTTPException(status_code=409, detail="Email already exists")

    user_data = data.model_dump()
    user_data["password"] = hash_password(user_data.pop("password"))

    user = User(**user_data)
    user.role = User.BaseUserRole.CUSTOMER

    await Users.create(db=db, obj=user)

    access, refresh = await create_tokens(user=user)

    await db.commit()
    return {
        "access_token": access,
        "refresh_token": refresh
    }


@auth_routes.post("/login", response_model=JWTResponse)
async def login_user(
    data: UserLogin,
    db: AsyncSession = Depends(get_session)
):
    stmt = select(User).where(User.email == data.email)

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(
        hash=user.password,
        password=data.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access, refresh = await create_tokens(user)

    return {
        "access_token": access,
        "refresh_token": refresh
    }


@auth_routes.post("/refresh", response_model=JWTResponse)
async def refresh_token(
    data: JWTRefresh,
    db: AsyncSession = Depends(get_session)
):
    try:
        user = await claim_token(db=db, token=data.refresh_token, token_type="refresh")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="User does not exist."
        )

    access, refresh = await create_tokens(user)
    return {"access_token": access, "refresh_token": refresh}