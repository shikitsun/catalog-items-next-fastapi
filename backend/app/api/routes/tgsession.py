from fastapi import APIRouter
from pydantic import BaseModel
from httpx import AsyncClient
from starlette.responses import JSONResponse

from app.core.config import get_settings

settings = get_settings()
router = APIRouter()

class InitDataModel(BaseModel):
    initData: str

@router.post("/verify")
async def verify(data: InitDataModel):
    async with AsyncClient(timeout=5) as client:
        result = await client.post(
            f"{settings.bot_api_url}/validate",
            json={"initData": data.initData},
            # In create admin-token, but there is internal token
            headers={"X-Internal-Token": settings.internal_token},
        )

    return JSONResponse(
        status_code=result.status_code,
        content=result.json(),
    )
