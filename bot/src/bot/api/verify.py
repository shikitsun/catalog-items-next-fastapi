from os import getenv

from aiohttp import web
from aiogram.utils.web_app import safe_parse_webapp_init_data

from bot.core.config import TOKEN, WEB_APP_PORT, INTERNAL_TOKEN


async def verify(request: web.Request):
    try:
        if request.headers['X-Internal-Token'] != INTERNAL_TOKEN:
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


async def init_web_app():
    app = web.Application()
    app.router.add_post("/validate", verify)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", WEB_APP_PORT).start()
    return runner
