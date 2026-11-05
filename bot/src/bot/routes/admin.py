from os import getenv
from io import BytesIO

from aiogram import Bot
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from httpx import AsyncClient

from bot.core.config import API_URL, INTERNAL_TOKEN

ADMIN_IDS = frozenset([int(value) for value in getenv("BOT_ADMIN_IDS", "").split(",") if value.strip()])

class AddItemCtx(StatesGroup):
    waiting_for_item_data = State()

admin_router = Router(name="admin")
admin_router.message.filter(F.from_user.id.in_(ADMIN_IDS))
admin_router.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))

@admin_router.message(Command("Add"))
async def add(message: Message, state: FSMContext) -> None:
    await state.set_state(AddItemCtx.waiting_for_item_data)
    await message.answer("Add title and single image of item")

@admin_router.message(AddItemCtx.waiting_for_item_data, F.photo)
async def receive(message: Message, state: FSMContext, bot: Bot) -> None:
    title = (message.caption or message.text or "").strip()

    if not title:
        await message.answer("Please add text to photo as plain message or caption to photo")
        return

    image = BytesIO()
    await bot.download(message.photo[-1].file_id, destination=image)
    image.seek(0)

    await message.answer(f"Starting uploading ${title} to server...")

    async with AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{API_URL}/items",
            data={"title": title},
            files={"file": ("photo.jpg", image, "image/jpeg")},
            # X-Admin-Token used for authentication purposes (between bot and backend)
            # X-Admin-UserId could be used for track which admin are added certain items
            # For now it don't are active used, but showing possibility there
            headers={"X-Admin-Token": INTERNAL_TOKEN, "X-Admin-UserId": message.from_user.id}
        )
        # Could be attached retry mechanic as well, but keep it simple for now
        await state.clear()
        try:
            response.raise_for_status()
        # Don't handle specific errors for now
        except:
            await message.edit_text(f"Failed to save item with title: {title}")
        else:
            await message.edit_text(f"Successfully saved as ${title}")


@admin_router.message(AddItemCtx.waiting_for_item_data)
async def not_a_photo(message: Message) -> None:
    await message.answer("No image are detected. Please, attach single photo with text or caption")
