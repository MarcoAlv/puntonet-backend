import uvicorn
from fastapi import FastAPI
from app.config import base
from app.lifespan import lifespan
from app.routes import load_routes
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
        title=base.APP_NAME,
        lifespan=lifespan
    )

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_routes(app=app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", workers=1, log_level="debug")
