import httpx
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings

router = Router()


class ReviewStates(StatesGroup):
    rating = State()
    comment = State()


@router.callback_query(F.data.startswith("review_"))
async def review_start(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    product_id, order_id = parts[1], parts[2]
    await state.update_data(product_id=product_id, order_id=order_id)

    builder = InlineKeyboardBuilder()
    for star in range(1, 6):
        label = "⭐" * star
        builder.button(text=label, callback_data=f"stars_{star}")
    builder.button(text="🔙 Cancel", callback_data="my_orders")
    builder.adjust(5)

    await callback.message.edit_text(
        "⭐ <b>Leave a Review</b>\n\nHow many stars would you like to give?",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(ReviewStates.rating)
    await callback.answer()


@router.callback_query(F.data.startswith("stars_"))
async def review_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.replace("stars_", ""))
    await state.update_data(rating=rating)
    await callback.message.edit_text(
        f"⭐ You selected <b>{rating} {'⭐' * rating}</b>\n\n"
        "Now send me your <b>comment</b> (or /skip to leave no comment):"
    )
    await state.set_state(ReviewStates.comment)
    await callback.answer()


@router.message(ReviewStates.comment)
async def review_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    comment = message.text if message.text != "/skip" else None
    await submit_review(message, state, data, comment)


async def submit_review(message: Message, state: FSMContext, data: dict, comment: str | None):
    payload = {
        "product_id": data["product_id"],
        "order_id": data["order_id"],
        "buyer_telegram_id": message.from_user.id,
        "rating": data["rating"],
        "comment": comment,
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{settings.backend_url}/reviews", json=payload, timeout=15)
    except Exception:
        await message.answer("❌ Service unavailable. Failed to submit review.\nPlease try again later.")
        await state.clear()
        return

    if resp.status_code == 201:
        await message.answer(
            "✅ <b>Review submitted!</b>\n\n"
            f"Rating: {'⭐' * data['rating']}\n"
            f"Comment: {comment or '(no comment)'}\n\n"
            "Thank you for your feedback!"
        )
    else:
        await message.answer("❌ Failed to submit review. Please try again later.")

    await state.clear()
