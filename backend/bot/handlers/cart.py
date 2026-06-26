import httpx
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings

router = Router()

user_carts: dict[int, list[dict]] = {}


class CheckoutStates(StatesGroup):
    name = State()
    phone = State()
    address = State()
    note = State()


@router.callback_query(F.data.startswith("addcart_"))
async def add_to_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    prod_id = callback.data.replace("addcart_", "")

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.backend_url}/products/{prod_id}")
        if resp.status_code != 200:
            await callback.answer("Product not available", show_alert=True)
            return
        product = resp.json()

    if user_id not in user_carts:
        user_carts[user_id] = []
    user_carts[user_id].append(
        {"product_id": product["id"], "name": product["name"], "price": product["price"], "quantity": 1}
    )

    await callback.answer(f"✅ Added: {product['name']}", show_alert=True)


@router.callback_query(F.data == "view_cart")
async def view_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    items = user_carts.get(user_id, [])

    if not items:
        await callback.message.edit_text(
            "🛒 Your cart is empty.\nBrowse products and add items!",
            reply_markup=InlineKeyboardBuilder()
            .button(text="Browse Products", callback_data="browse_products")
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    total = sum(item["price"] * item["quantity"] for item in items)
    lines = ["<b>🛒 Your Cart</b>\n"]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['name']} x{item['quantity']} — {item['price'] * item['quantity']:,.0f} MMK")
    lines.append(f"\n<b>Total: {total:,.0f} MMK</b>")

    builder = InlineKeyboardBuilder()
    builder.button(text="Checkout ✅", callback_data="checkout")
    builder.button(text="Clear Cart 🗑️", callback_data="clear_cart")
    builder.button(text="🔙 Back", callback_data="back_main")
    builder.adjust(1)

    await callback.message.edit_text("\n".join(lines), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    user_carts.pop(callback.from_user.id, None)
    await callback.message.edit_text("🗑️ Cart cleared.")
    await callback.answer()


@router.callback_query(F.data == "checkout")
async def checkout_start(callback: CallbackQuery, state: FSMContext):
    items = user_carts.get(callback.from_user.id, [])
    if not items:
        await callback.answer("Cart is empty!", show_alert=True)
        return

    await callback.message.edit_text(
        "📋 <b>Checkout Step 1/4</b>\n\nWhat is your <b>full name</b>?"
    )
    await state.set_state(CheckoutStates.name)
    await callback.answer()


@router.message(CheckoutStates.name)
async def checkout_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Step 2/4: What is your <b>phone number</b>?")
    await state.set_state(CheckoutStates.phone)


@router.message(CheckoutStates.phone)
async def checkout_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Step 3/4: What is your <b>shipping address</b>?")
    await state.set_state(CheckoutStates.address)


@router.message(CheckoutStates.address)
async def checkout_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer(
        "Step 4/4: Any <b>notes</b> for the seller?\n"
        "(Send /skip if none)"
    )
    await state.set_state(CheckoutStates.note)


@router.message(CheckoutStates.note)
async def checkout_finish(message: Message, state: FSMContext):
    data = await state.update_data(note=message.text if message.text != "/skip" else "")
    await place_order(message, state, data)


async def place_order(message: Message, state: FSMContext, data: dict):
    user_id = message.from_user.id
    items = user_carts.get(user_id, [])

    if not items:
        await message.answer("Your cart is empty.")
        await state.clear()
        return

    if not items:
        return

    seller_id = items[0].get("seller_id")
    if not seller_id:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.backend_url}/products/{items[0]['product_id']}")
            if resp.status_code == 200:
                seller_id = resp.json()["seller_id"]

    payload = {
        "seller_id": seller_id,
        "buyer_telegram_id": user_id,
        "buyer_name": data.get("name", ""),
        "buyer_phone": data.get("phone", ""),
        "shipping_address": data.get("address", ""),
        "note": data.get("note", ""),
        "payment_method": "cod",
        "items": [{"product_id": i["product_id"], "quantity": i["quantity"], "price": i["price"]} for i in items],
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{settings.backend_url}/orders", json=payload)

    if resp.status_code == 201:
        order = resp.json()
        user_carts.pop(user_id, None)
        await message.answer(
            f"✅ <b>Order placed!</b>\n\n"
            f"🆔 Order ID: <code>{order['id'][:8]}...</code>\n"
            f"💰 Total: {order['total']:,.0f} MMK\n"
            f"📦 Status: <b>{order['status']}</b>\n\n"
            "The seller will contact you soon!",
        )
        try:
            from bot.keyboards.menu import main_menu_keyboard
            await message.answer("What would you like to do next?", reply_markup=main_menu_keyboard())
        except Exception:
            pass
    else:
        await message.answer("❌ Order failed. Please try again later.")

    await state.clear()
