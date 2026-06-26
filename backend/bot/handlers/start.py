from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.menu import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Welcome to <b>fbtiktokcommerce</b>! 🛍️\n\n"
        "Myanmar's organized marketplace for Facebook & TikTok sellers.\n\n"
        "👋 <b>Buyer</b> — Browse products, place orders, track deliveries\n"
        "🏪 <b>Seller</b> — Register your shop, manage products & orders\n\n"
        "Use the menu below to get started.",
        reply_markup=main_menu_keyboard(),
    )
