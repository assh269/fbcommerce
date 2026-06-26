from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ReviewCreate(BaseModel):
    product_id: UUID
    order_id: Optional[UUID] = None
    buyer_telegram_id: int
    rating: int
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: UUID
    product_id: UUID
    order_id: Optional[UUID]
    buyer_telegram_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
