from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
async def list_orders(
    seller_id: UUID | None = None,
    buyer_tg_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())
    if seller_id:
        stmt = stmt.where(Order.seller_id == seller_id)
    if buyer_tg_id:
        stmt = stmt.where(Order.buyer_telegram_id == buyer_tg_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    total = sum(item.price * item.quantity for item in data.items)
    order = Order(
        seller_id=data.seller_id,
        buyer_telegram_id=data.buyer_telegram_id,
        buyer_name=data.buyer_name,
        buyer_phone=data.buyer_phone,
        shipping_address=data.shipping_address,
        payment_method=data.payment_method,
        note=data.note,
        total=total,
    )
    db.add(order)
    await db.flush()
    for item_data in data.items:
        item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=item_data.price,
        )
        db.add(item)
    await db.commit()
    await db.refresh(order)
    stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order.id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(order_id: UUID, data: OrderStatusUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = data.status
    await db.commit()
    await db.refresh(order)
    return order
