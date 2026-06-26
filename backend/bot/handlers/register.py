import httpx
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.config import settings
from bot.keyboards.menu import main_menu_keyboard

router = Router()


class RegisterStates(StatesGroup):
    business_name = State()
    phone = State()
    description = State()


@router.callback_query(F.data == "register_seller")
async def register_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Let's set up your shop! 🏪\n\n"
        "Step 1/3: What is your <b>shop/business name</b>?"
    )
    await state.set_state(RegisterStates.business_name)
    await callback.answer()


@router.message(RegisterStates.business_name)
async def register_business_name(message: Message, state: FSMContext):
    await state.update_data(business_name=message.text)
    await message.answer(
        "Step 2/3: What is your <b>phone number</b>?\n"
        "(Buyers will use this to contact you)"
    )
    await state.set_state(RegisterStates.phone)


@router.message(RegisterStates.phone)
async def register_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(
        "Step 3/3: Tell us about your shop 📝\n"
        "(What do you sell? Any special notes for buyers?)"
    )
    await state.set_state(RegisterStates.description)


@router.message(RegisterStates.description)
async def register_description(message: Message, state: FSMContext):
    data = await state.update_data(description=message.text)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.backend_url}/sellers",
            json={
                "telegram_id": message.from_user.id,
                "username": message.from_user.username,
                "business_name": data["business_name"],
                "phone": data["phone"],
                "description": data["description"],
            },
        )
    if resp.status_code == 201:
        await message.answer(
            "✅ <b>Shop registered successfully!</b>\n\n"
            f"🏪 {data['business_name']}\n"
            f"📞 {data['phone']}\n\n"
            "You can now:\n"
            "• Add products via /addproduct\n"
            "• View orders via /myorders\n"
            "• Manage your catalog in the web dashboard",
            reply_markup=main_menu_keyboard(),
        )
    else:
        err = resp.json()
        await message.answer(
            f"❌ Registration failed: {err.get('detail', 'Unknown error')}\n"
            "Try again with /start",
            reply_markup=main_menu_keyboard(),
        )
    await state.clear()
