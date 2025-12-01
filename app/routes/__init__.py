from app.config import base
from fastapi import APIRouter, FastAPI
from app.routes.ws.chat import chat_routes
from app.routes.http.auth import auth_routes
from app.routes.http.user import user_routes
from app.routes.http.store import store_routes


h_routers: list[APIRouter] = [auth_routes, user_routes, store_routes]

w_routers: list[APIRouter] = [chat_routes]


def load_routes(app: FastAPI):
    for r in h_routers:
        app.include_router(router=r, prefix=f"/api/v{base.APP_VERSION}")
    for r in w_routers:
        app.include_router(router=r, prefix=f"/ws/v{base.APP_VERSION}")
