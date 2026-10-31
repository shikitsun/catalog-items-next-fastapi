from fastapi import FastAPI

from app.api.routes import items
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
