from app.dependencies.auth import basic_permission_dependency
from app.schemas.users import UserProfile
from fastapi import APIRouter, Depends
from app.models.users import User


user_routes = APIRouter(prefix="/user")


@user_routes.get("/profile", response_model=UserProfile)
def get_user_profile(user: User = Depends(basic_permission_dependency([]))):
    return user