from fastapi import FastAPI
from app.core.ws import broadcaster
from app.core.db.sessionmanager import sessionmanager
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    await broadcaster.connect()
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()
    await broadcaster.disconnect()
