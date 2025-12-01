from app.dependencies.auth import basic_permission_dependency
from app.schemas.users import UserProfile, UserProfileUpdate
from app.schemas.store import CreateProducto
from app.core.db.sessionmanager import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.models.users import User


store_routes = APIRouter(prefix="/store", tags=["Store"])


@store_routes.get("/profile", response_model=UserProfile)
def create_product(producto: CreateProducto, user: User = Depends(basic_permission_dependency([]))):
    return user