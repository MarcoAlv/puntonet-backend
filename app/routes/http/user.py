from app.dependencies.auth import basic_permission_dependency
from app.schemas.users import UserProfile, UserProfileUpdate
from app.core.db.sessionmanager import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.models.users import User


user_routes = APIRouter(prefix="/user", tags=["User"])


@user_routes.get("/profile", response_model=UserProfile)
def get_user_profile(user: User = Depends(basic_permission_dependency([]))):
    return user


@user_routes.put("/profile", response_model=UserProfile)
async def set_user_profile(
    new_user: UserProfileUpdate ,
    user: User = Depends(basic_permission_dependency([])),
    db: AsyncSession = Depends(get_session)
):
    data = new_user.model_dump(exclude_unset=True)

    if user.store_name:
        data.pop("store_name", None)

    for field, value in data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user