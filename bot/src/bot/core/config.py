from os import getenv

APP_URL = getenv("APP_URL")
API_URL = (getenv("API_URL") or "").strip()
TOKEN = getenv("BOT_TOKEN")
WEB_APP_PORT = int(getenv("BOT_WEB_APP_PORT") or "62402")
INTERNAL_TOKEN = getenv("INTERNAL_TOKEN")

REDIS_URL = getenv("REDIS_URL") or "redis://redis:6379/0"

WEBHOOK_BASE = (getenv("WEBHOOK_BASE") or "").rstrip("/")
WEBHOOK_PATH = getenv("WEBHOOK_PATH") or "/webhook"
WEBHOOK_SECRET = getenv("WEBHOOK_SECRET") or ""
