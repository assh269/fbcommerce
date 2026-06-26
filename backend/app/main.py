from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import categories, orders, products, reviews, sellers
from bot.handlers import cart, catalog, orders as bot_orders, register, reviews as bot_reviews, start

bot: Bot | None = None
dp: Dispatcher | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot, dp
    try:
        await init_db()
    except Exception as e:
        print(f"Database init failed (non-fatal): {e}")
    if settings.bot_token:
        bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        dp = Dispatcher()
        dp.include_routers(
            start.router, register.router, catalog.router, cart.router, bot_orders.router, bot_reviews.router,
        )
        webhook_url = f"{settings.backend_url}/api/webhook"
        try:
            await bot.set_webhook(url=webhook_url)
        except Exception as e:
            print(f"Webhook setup failed (non-fatal): {e}")
    yield
    # Don't close bot session — it's reused across invocations on warm instances


app = FastAPI(title="fbtiktokcommerce", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sellers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(categories.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    if not bot or not dp:
        return {"ok": False, "error": "Bot not initialized"}
    try:
        body = await request.json()
        update = Update.model_validate(body)
        await dp.feed_update(bot, update)
        return {"ok": True}
    except Exception as e:
        import traceback
        print(f"Webhook error: {e}\n{traceback.format_exc()}")
        return {"ok": False, "error": str(e)}
