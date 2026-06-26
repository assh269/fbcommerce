import httpx
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings

router = Router()


@router.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.backend_url}/orders?buyer_tg_id={user_id}")

    if resp.status_code != 200 or not resp.json():
        await callback.message.edit_text(
            "📭 You have no orders yet.\nBrowse products and place your first order!",
            reply_markup=InlineKeyboardBuilder()
            .button(text="Browse Products", callback_data="browse_products")
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    orders = resp.json()
    lines = ["<b>📋 Your Orders</b>\n"]
    for o in orders[:5]:
        lines.append(
            f"🆔 {o['id'][:8]}... | {o['total']:,.0f} MMK | <b>{o['status']}</b>"
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Back", callback_data="back_main")
    await callback.message.edit_text("\n".join(lines), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "seller_orders")
async def seller_orders(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.backend_url}/sellers/telegram/{user_id}")

    if resp.status_code != 200:
        await callback.message.edit_text(
            "❌ You are not registered as a seller.\nRegister first!",
            reply_markup=InlineKeyboardBuilder()
            .button(text="Register", callback_data="register_seller")
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    seller = resp.json()
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.backend_url}/orders?seller_id={seller['id']}")

    orders = resp.json() if resp.status_code == 200 else []
    if not orders:
        await callback.message.edit_text(
            "📭 No orders received yet.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    lines = ["<b>📋 Incoming Orders</b>\n"]
    for o in orders[:10]:
        lines.append(
            f"🆔 {str(o['id'])[:8]}...\n"
            f"👤 {o.get('buyer_name', 'Unknown')}\n"
            f"💰 {o['total']:,.0f} MMK\n"
            f"📌 <b>{o['status']}</b>\n"
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Refresh", callback_data="seller_orders")
    builder.button(text="🔙 Back", callback_data="back_main")
    builder.adjust(1)

    await callback.message.edit_text("\n".join(lines), reply_markup=builder.as_markup())
    await callback.answer()
