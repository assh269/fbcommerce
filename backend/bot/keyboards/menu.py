from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Browse Products", callback_data="browse_products")
    builder.button(text="View Cart 🛒", callback_data="view_cart")
    builder.button(text="My Orders", callback_data="my_orders")
    builder.button(text="Register as Seller", callback_data="register_seller")
    builder.button(text="Seller Dashboard", callback_data="seller_orders")
    builder.button(text="Open Web Dashboard 🌐", url="http://localhost:5173")
    builder.adjust(2)
    return builder.as_markup()
