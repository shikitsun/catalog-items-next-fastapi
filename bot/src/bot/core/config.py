from os import getenv

APP_URL = getenv("APP_URL")
API_URL = getenv("API_URL").strip()
TOKEN = getenv("BOT_TOKEN")
WEB_APP_PORT = int(getenv("BOT_WEB_APP_PORT") or "62402")
INTERNAL_TOKEN = getenv("INTERNAL_TOKEN")
