from bot.core.config import API_URL
from httpx import AsyncClient


async def get_items_list() -> list:
    async with AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{API_URL}/items/all",
        )
        response.raise_for_status()
        return response.json()