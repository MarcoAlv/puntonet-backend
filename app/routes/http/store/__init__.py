from fastapi import APIRouter

store_routes = APIRouter(prefix="/store", tags=["Store"])

from .products import *