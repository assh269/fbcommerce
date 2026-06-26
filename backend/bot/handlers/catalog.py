import httpx
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings

router = Router()


async def fetch_products(seller_id: int | None = None):
    url = f"{settings.backend_url}/products"
    if seller_id:
        url += f"?seller_id={seller_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=15)
        return resp.json() if resp.status_code == 200 else []


def product_card(product: dict) -> str:
    name = product["name"]
    price = product["price"]
    currency = product.get("currency", "MMK")
    stock = product.get("stock", 0)
    desc = product.get("description", "")
    return (
        f"<b>{name}</b>\n"
        f"💰 {price:,.0f} {currency}\n"
        f"📦 In stock: {stock}\n"
        f"{'📝 ' + desc[:200] if desc else ''}"
    )


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
    cat_id = callback.data.replace("cat_", "")
    try:
        products = await fetch_products()
    except Exception:
        products = []

    if cat_id != "all":
        products = [p for p in products if str(p.get("category_id", "")) == cat_id]

    if not products:
        await callback.message.edit_text(
            "No products found in this category.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="🔙 Back", callback_data="browse_products")
            .as_markup(),
        )
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    for p in products[:10]:
        builder.button(text=f"{p['name']} — {p['price']:,.0f} MMK", callback_data=f"prod_{p['id']}")
    builder.button(text="🔙 Categories", callback_data="browse_products")
    builder.adjust(1)

    await callback.message.edit_text(
        f"📦 <b>Products ({len(products)})</b>\n\nTap a product for details:",
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

    builder = InlineKeyboardBuilder()
    builder.button(text="Add to Cart 🛒", callback_data=f"addcart_{prod_id}")
    builder.button(text="🔙 Back", callback_data="browse_products")
    builder.adjust(1)

    await callback.message.edit_text(
        product_card(product),
        reply_markup=builder.as_markup(),
    )
    await callback.answer()
