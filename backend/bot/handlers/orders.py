import httpx
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings

router = Router()

review_tokens: dict[str, tuple[str, str]] = {}
_token_counter = 0
user_order_pages: dict[int, int] = {}
ORDER_PAGE_SIZE = 5


def _make_review_token(product_id: str, order_id: str) -> str:
    global _token_counter
    _token_counter += 1
    token = f"rtok{_token_counter}"
    review_tokens[token] = (product_id, order_id)
    return token


@router.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_order_pages[user_id] = 0
    await show_orders_page(callback, user_id, 0)


async def show_orders_page(callback: CallbackQuery, user_id: int, page: int):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.backend_url}/orders?buyer_tg_id={user_id}", timeout=15)
    except Exception:
        await callback.message.edit_text(
            "❌ Service unavailable. Please try again later.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    if resp.status_code != 200:
        await callback.message.edit_text(
            "📭 You have no orders yet.\nBrowse products and place your first order!",
            reply_markup=InlineKeyboardBuilder()
            .button(text="Browse Products", callback_data="browse_products")
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    try:
        orders = resp.json()
    except Exception:
        orders = []

    if not orders:
        await callback.message.edit_text(
            "📭 You have no orders yet.\nBrowse products and place your first order!",
            reply_markup=InlineKeyboardBuilder()
            .button(text="Browse Products", callback_data="browse_products")
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    total = len(orders)
    start = page * ORDER_PAGE_SIZE
    end = start + ORDER_PAGE_SIZE
    page_orders = orders[start:end]
    has_next = end < total
    has_prev = page > 0

    builder = InlineKeyboardBuilder()
    for o in page_orders:
        oid = o.get("id", "?")
        oid_short = str(oid)[:8]
        total_val = o.get("total", 0)
        total_str = f"{total_val:,.0f}" if isinstance(total_val, (int, float)) else str(total_val)
        label = f"🆔 {oid_short}... | {total_str} MMK | {o.get('status', '?')}"
        builder.button(text=label, callback_data=f"order_{oid}")
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="◀️ Prev", callback_data=f"ordpage_{page - 1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"ordpage_{page + 1}"))
    if nav:
        builder.row(*nav)
    builder.button(text="🔙 Back", callback_data="back_main")

    await callback.message.edit_text(
        f"<b>📋 Your Orders</b> (page {page + 1}/{((total - 1) // ORDER_PAGE_SIZE) + 1})\n\nTap an order to view details or leave a review:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ordpage_"))
async def order_page_nav(callback: CallbackQuery):
    user_id = callback.from_user.id
    page = int(callback.data.replace("ordpage_", ""))
    user_order_pages[user_id] = page
    await show_orders_page(callback, user_id, page)


@router.callback_query(F.data.startswith("order_"))
async def order_detail(callback: CallbackQuery):
    order_id = callback.data.replace("order_", "")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.backend_url}/orders/{order_id}", timeout=15)
    except Exception:
        await callback.answer("Service unavailable. Try again later.", show_alert=True)
        return

    if resp.status_code != 200:
        await callback.answer("Order not found", show_alert=True)
        return

    try:
        o = resp.json()
    except Exception:
        await callback.answer("Invalid response from server", show_alert=True)
        return

    oid_short = str(o.get("id", ""))[:8]
    total_val = o.get("total", 0)
    total_str = f"{total_val:,.0f}" if isinstance(total_val, (int, float)) else str(total_val)
    lines = [
        f"<b>Order Details</b>\n",
        f"🆔 {oid_short}...",
        f"💰 {total_str} MMK",
        f"📌 <b>{o.get('status', 'N/A')}</b>",
        f"👤 {o.get('buyer_name', 'N/A')}",
        f"📞 {o.get('buyer_phone', 'N/A')}",
        f"📍 {o.get('shipping_address', 'N/A')}",
    ]
    if o.get("note"):
        lines.append(f"📝 {o['note']}")

    builder = InlineKeyboardBuilder()
    items = o.get("items") or []
    for item in items:
        pid = item.get("product_id") or item.get("id")
        pname = item.get("name", item.get("product_name", "Product"))
        token = _make_review_token(pid, order_id)
        builder.button(text=f"⭐ Review {pname}", callback_data=f"rev_{token}")
    builder.button(text="🔙 Back", callback_data="my_orders")
    builder.adjust(1)

    await callback.message.edit_text("\n".join(lines), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "seller_orders")
async def seller_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.backend_url}/sellers/telegram/{user_id}", timeout=15)
    except Exception:
        await callback.message.edit_text(
            "❌ Service unavailable. Please try again later.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

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

    try:
        seller = resp.json()
    except Exception:
        await callback.message.edit_text(
            "❌ Service error. Try again later.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.backend_url}/orders?seller_id={seller.get('id')}", timeout=15)
    except Exception:
        await callback.message.edit_text(
            "❌ Service unavailable. Please try again later.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    try:
        orders = resp.json() if resp.status_code == 200 else []
    except Exception:
        orders = []

    if not orders:
        await callback.message.edit_text(
            "📭 No orders received yet.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    for o in orders[:10]:
        oid = o.get("id", "?")
        oid_short = str(oid)[:8]
        total_val = o.get("total", 0)
        total_str = f"{total_val:,.0f}" if isinstance(total_val, (int, float)) else str(total_val)
        label = f"🆔 {oid_short}... | {o.get('buyer_name', '?')} | {total_str} MMK | {o.get('status', '?')}"
        builder.button(text=label, callback_data=f"sord_{oid}")
    builder.button(text="🔄 Refresh", callback_data="seller_orders")
    builder.button(text="🔙 Back", callback_data="back_main")
    builder.adjust(1)

    await callback.message.edit_text(
        "<b>📋 Incoming Orders</b>\n\nTap an order for details:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sord_"))
async def seller_order_detail(callback: CallbackQuery):
    order_id = callback.data.replace("sord_", "")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.backend_url}/orders/{order_id}", timeout=15)
    except Exception:
        await callback.answer("Service unavailable. Try again later.", show_alert=True)
        return

    if resp.status_code != 200:
        await callback.answer("Order not found", show_alert=True)
        return

    try:
        o = resp.json()
    except Exception:
        await callback.answer("Invalid response", show_alert=True)
        return

    oid_short = str(o.get("id", ""))[:8]
    total_val = o.get("total", 0)
    total_str = f"{total_val:,.0f}" if isinstance(total_val, (int, float)) else str(total_val)
    lines = [
        f"<b>Order Details</b>\n",
        f"🆔 {oid_short}...",
        f"💰 {total_str} MMK",
        f"📌 <b>{o.get('status', 'N/A')}</b>",
        f"👤 Buyer: {o.get('buyer_name', 'N/A')}",
        f"📞 {o.get('buyer_phone', 'N/A')}",
        f"📍 {o.get('shipping_address', 'N/A')}",
    ]
    if o.get("note"):
        lines.append(f"📝 Note: {o['note']}")

    items = o.get("items") or []
    if items:
        lines.append("\n<b>Items:</b>")
        for item in items:
            pname = item.get("name", item.get("product_name", "Product"))
            qty = item.get("quantity", 1)
            iprice = item.get("price", 0)
            iprice_str = f"{iprice:,.0f}" if isinstance(iprice, (int, float)) else str(iprice)
            lines.append(f"• {pname} x{qty} — {iprice_str} MMK")

    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Back to Orders", callback_data="seller_orders")
    builder.adjust(1)

    await callback.message.edit_text("\n".join(lines), reply_markup=builder.as_markup())
    await callback.answer()
