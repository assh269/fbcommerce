from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int
    price: float


class OrderCreate(BaseModel):
    seller_id: UUID
    buyer_telegram_id: int
    buyer_name: Optional[str] = None
    buyer_phone: Optional[str] = None
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    note: Optional[str] = None
    items: list[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: str


class OrderItemOut(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: UUID
    seller_id: UUID
    buyer_telegram_id: int
    buyer_name: Optional[str]
    buyer_phone: Optional[str]
    shipping_address: Optional[str]
    total: float
    status: str
    payment_method: Optional[str]
    note: Optional[str]
    created_at: datetime
    items: list[OrderItemOut] = []

    class Config:
        from_attributes = True
