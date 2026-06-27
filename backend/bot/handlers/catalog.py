import httpx
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings

router = Router()

PAGE_SIZE = 10
user_pages: dict[int, dict] = {}


async def fetch_products(category_id: str | None = None):
    url = f"{settings.backend_url}/products"
    params = []
    if category_id and category_id != "all":
        params.append(f"category_id={category_id}")
    if params:
        url += "?" + "&".join(params)
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=15)
        return resp.json() if resp.status_code == 200 else []


def product_card(product: dict) -> str:
    name = product.get("name", "Unknown")
    price = product.get("price", 0)
    currency = product.get("currency", "MMK")
    stock = product.get("stock", 0)
    desc = product.get("description", "")
    images = product.get("images", [])
    img_url = images[0]["url"] if images else None
    lines = [f"<b>{name}</b>"]
    if img_url:
        lines.append(f"🖼️ <a href='{img_url}'>View Image</a>")
    lines.append(f"💰 {price:,.0f} {currency}")
    lines.append(f"📦 In stock: {stock}")
    if desc:
        lines.append(f"📝 {desc[:200]}")
    return "\n".join(lines)


@router.callback_query(F.data == "browse_products")
async def browse_categories(callback: CallbackQuery):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.backend_url}/categories", timeout=15)
            categories = resp.json() if resp.status_code == 200 else []
    except Exception:
        categories = []

    if not categories:
        await callback.message.edit_text(
            "No categories available right now. Try again later.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔙 Back", callback_data="back_main")
            .as_markup(),
        )
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat["name"], callback_data=f"cat_{cat['id']}")
    builder.button(text="All Products", callback_data="cat_all")
    builder.button(text="🔙 Back", callback_data="back_main")
    builder.adjust(2)

    await callback.message.edit_text(
        "📂 <b>Browse by Category</b>\n\nSelect a category:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat_"))
async def list_products(callback: CallbackQuery):
    user_id = callback.from_user.id
    cat_id = callback.data.replace("cat_", "")
    try:
        products = await fetch_products(cat_id if cat_id != "all" else None)
    except Exception:
        products = []

    if not products:
        await callback.message.edit_text(
            "No products found in this category.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔙 Back", callback_data="browse_products")
            .as_markup(),
        )
        await callback.answer()
        return

    user_pages[user_id] = {"cat_id": cat_id, "page": 0, "products": [p["id"] for p in products]}
    total = len(products)
    page = 0
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_products = products[start:end]
    has_next = end < total

    builder = InlineKeyboardBuilder()
    for p in page_products:
        builder.button(text=f"{p.get('name', '?')} — {p.get('price', 0):,.0f} MMK", callback_data=f"prod_{p['id']}")
    nav_row = []
    if has_next:
        nav_row.append(("Next ➡️", f"page_next_{cat_id}"))
    builder.button(text="🔙 Categories", callback_data="browse_products")
    builder.adjust(1)

    await callback.message.edit_text(
        f"📦 <b>Products</b> (page {page + 1}, {total} total)\n\nTap a product for details:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("page_next_"))
async def next_page(callback: CallbackQuery):
    user_id = callback.from_user.id
    cat_id = callback.data.replace("page_next_", "")
    user_data = user_pages.get(user_id, {})
    page = user_data.get("page", 0) + 1 if user_data.get("cat_id") == cat_id else 0

    try:
        products = await fetch_products(cat_id if cat_id != "all" else None)
    except Exception:
        products = []

    if not products:
        await callback.answer("No more products.", show_alert=True)
        return

    user_pages[user_id] = {"cat_id": cat_id, "page": page, "products": [p["id"] for p in products]}
    total = len(products)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_products = products[start:end]
    has_next = end < total

    builder = InlineKeyboardBuilder()
    for p in page_products:
        builder.button(text=f"{p.get('name', '?')} — {p.get('price', 0):,.0f} MMK", callback_data=f"prod_{p['id']}")
    if has_next:
        builder.button(text="Next ➡️", callback_data=f"page_next_{cat_id}")
    builder.button(text="🔙 Categories", callback_data="browse_products")
    builder.adjust(1)

    await callback.message.edit_text(
        f"📦 <b>Products</b> (page {page + 1}, {total} total)\n\nTap a product for details:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prod_"))
async def product_detail(callback: CallbackQuery):
    prod_id = callback.data.replace("prod_", "")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.backend_url}/products/{prod_id}", timeout=15)
    except Exception:
        await callback.answer("Service unavailable. Try again later.", show_alert=True)
        return

    if resp.status_code != 200:
        await callback.answer("Product not found", show_alert=True)
        return
    product = resp.json()

    try:
        async with httpx.AsyncClient() as client:
            rev_resp = await client.get(f"{settings.backend_url}/reviews/product/{prod_id}", timeout=10)
            reviews = rev_resp.json() if rev_resp.status_code == 200 else []
            avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else None
    except Exception:
        reviews = []
        avg_rating = None

    text = product_card(product)
    if avg_rating:
        text += f"\n⭐ <b>{avg_rating}</b> ({len(reviews)} reviews)"
    else:
        text += "\n⭐ No reviews yet"

    builder = InlineKeyboardBuilder()
    builder.button(text="Add to Cart 🛒", callback_data=f"addcart_{prod_id}")
    builder.button(text="🔙 Back", callback_data="browse_products")
    builder.adjust(1)

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
    )
    await callback.answer()
