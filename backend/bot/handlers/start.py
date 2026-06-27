from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.menu import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Welcome to <b>fbtiktokcommerce</b>! 🛍️\n\n"
        "Myanmar's organized marketplace for Facebook & TikTok sellers.\n\n"
        "👋 <b>Buyer</b> — Browse products, place orders\n"
        "🏪 <b>Seller</b> — Register your shop, manage orders\n\n"
        "Use the menu below to get started.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Cancelled. Returning to main menu.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "<b>Main Menu</b>\n\nChoose an option below:",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()
