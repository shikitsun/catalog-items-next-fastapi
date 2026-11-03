from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import items, tgsession
from app.core.config import get_settings
from app.services.file import init_bucket

settings = get_settings()

# https://fastapi.tiangolo.com/advanced/events/#use-case
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_bucket()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(tgsession.router, prefix="/tg", tags=["items"])

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
