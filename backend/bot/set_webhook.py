import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    webhook_url = f"{settings.backend_url}/webhook"
    result = await bot.set_webhook(url=webhook_url)
    print(f"Webhook set to {webhook_url}: {result}")
    info = await bot.get_webhook_info()
    print(f"Current webhook: {info.url}")
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
