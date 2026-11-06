from aiogram import Dispatcher, Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.core.config import INTERNAL_TOKEN, TOKEN, WEBHOOK_BASE, WEBHOOK_PATH, WEBHOOK_SECRET, WEB_APP_PORT


async def verify(request: web.Request):
    try:
        if request.headers["X-Internal-Token"] != INTERNAL_TOKEN:
            return web.json_response({"error": "Unknown internal token"}, status=401)

        body = await request.json()
        data = safe_parse_webapp_init_data(
            token=TOKEN,
            init_data=body["initData"],
        )
    except (ValueError, KeyError, TypeError):
        return web.json_response({"error": "Invalid init data"}, status=401)

    # Also check data.auth_date is recent enough for your app.
    return web.json_response({
        "user_id": data.user.id if data.user else None
    })

async def init_web_app(*, dp: Dispatcher, bot: Bot) -> web.AppRunner:
    app = web.Application()
    app.router.add_post("/validate", verify)

    if WEBHOOK_BASE:
        SimpleRequestHandler(dp, bot, secret_token=WEBHOOK_SECRET).register(
            app, path=WEBHOOK_PATH
        )
        setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)

    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", WEB_APP_PORT).start()

    return runner
