import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from bot.api.items import get_items_list
from bot.api.verify import init_web_app
from bot.core.config import (
    APP_URL,
    REDIS_URL,
    TOKEN,
    WEBHOOK_BASE,
    WEBHOOK_PATH,
    WEBHOOK_SECRET,
)
from bot.routes.admin import admin_router

# Bot token can be obtained via https://t.me/BotFather

dp = Dispatcher(storage=RedisStorage.from_url(REDIS_URL))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Open App", web_app=WebAppInfo(url=APP_URL))]
        ]
    )

    items = await get_items_list()

    await message.answer(
        f"Available {len(items)}" if len(items) else "No items available yet",
        reply_markup=keyboard,
    )


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(admin_router)

    runner = await init_web_app(dp=dp, bot=bot)

    # And the run events dispatching
    try:
        if WEBHOOK_BASE:
            await bot.set_webhook(
                f"{WEBHOOK_BASE}{WEBHOOK_PATH}",
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True,
            )
            await asyncio.Event().wait()
        else:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
